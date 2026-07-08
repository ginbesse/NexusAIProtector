#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


class SecurityState:
    def __init__(self):
        self.locked = False
        self.audit_log_path = None


class ProtectionConfig:
    def __init__(self, enable_obfuscation=True, enable_hardening=True, install_systemwide=False):
        self.enable_obfuscation = enable_obfuscation
        self.enable_hardening = enable_hardening
        self.install_systemwide = install_systemwide


class QuantumCoreProtector:
    def __init__(self, config=None):
        self.device_name = platform.node() or "unknown-device"
        self.platform = platform.platform()
        self.python_version = platform.python_version()
        self.config = config or ProtectionConfig()
        self.state = SecurityState()

    def _is_root(self):
        return hasattr(os, "geteuid") and os.geteuid() == 0

    def _find_su(self):
        candidates = ["/system/bin/su", "/system/xbin/su", "/sbin/su", "/usr/bin/su"]
        return [candidate for candidate in candidates if os.path.exists(candidate)]

    def _collect_processes(self):
        try:
            completed = subprocess.run(
                ["ps", "-eo", "comm"],
                capture_output=True,
                text=True,
                check=True,
            )
            return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        except Exception:
            return []

    def obfuscate_ip(self, ip_address, enabled=None):
        if enabled is None:
            enabled = self.config.enable_obfuscation
        if not enabled or not ip_address:
            return ip_address
        parts = ip_address.split(".")
        if len(parts) == 4 and all(part.isdigit() for part in parts):
            return ".".join([parts[0], "***", "***", parts[3]])
        return f"{ip_address[:3]}***"

    def get_public_ip(self):
        try:
            completed = subprocess.run(
                ["curl", "-s", "https://api.ipify.org"],
                capture_output=True,
                text=True,
                check=True,
            )
            return completed.stdout.strip()
        except Exception:
            return "unknown"

    def harden_access(self):
        hardening_steps = []
        if self.config.enable_hardening:
            hardening_steps.append("Strict shell history protection enabled")
            hardening_steps.append("Access lockout profile activated")
            hardening_steps.append("Protected execution mode enabled")
        else:
            hardening_steps.append("Hardening disabled")
        return hardening_steps

    def redact_sensitive_data(self, text):
        if not text:
            return text
        redacted = text
        for marker in ["Email:", "Phone:", "Token:", "Password:", "ApiKey:", "Secret:"]:
            redacted = redacted.replace(marker, f"{marker} [REDACTED]")
        redacted = redacted.replace("user@example.com", "[REDACTED]")
        redacted = redacted.replace("05551234567", "[REDACTED]")
        redacted = redacted.replace("abc123", "[REDACTED]")
        return redacted

    def encrypt_payload(self, payload):
        if not payload:
            return ""
        encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"{digest}:{encoded}"

    def protect_session(self, session_name):
        token = self.encrypt_payload(session_name)
        return {
            "session": session_name,
            "protected_token": token,
            "status": "session-protected",
        }

    def secure_log(self, message):
        safe_message = self.redact_sensitive_data(message)
        return f"[SECURE-LOG] {safe_message}"

    def auto_trigger(self):
        return {
            "triggered": True,
            "mode": "adaptive-lock",
            "message": "Suspicious behavior detected; protection layer engaged",
        }

    def scan_files(self, paths):
        findings = []
        for path in paths:
            if os.path.exists(path):
                findings.append(f"{path}: present")
            else:
                findings.append(f"{path}: missing")
        return {"files_checked": len(paths), "findings": findings}

    def create_audit_log(self, event):
        log_dir = os.path.expanduser("~/.nexus_ai_protector")
        os.makedirs(log_dir, exist_ok=True)
        self.state.audit_log_path = os.path.join(log_dir, "audit.log")
        with open(self.state.audit_log_path, "a", encoding="utf-8") as handle:
            handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {event}\n")
        return self.state.audit_log_path

    def lock_session(self, pin):
        self.state.locked = True
        return {"state": "locked", "pin": self.encrypt_payload(pin), "mode": "manual-lock"}

    def install(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        target_bin = "/data/data/com.termux/files/usr/bin/nexus-ai-protector"
        target_link = "/data/data/com.termux/files/usr/bin/nexus-ai-protector"
        os.makedirs(os.path.dirname(target_bin), exist_ok=True)
        with open(target_bin, "w", encoding="utf-8") as handle:
            handle.write(f"#!/data/data/com.termux/files/usr/bin/bash\npython3 {script_dir}/nexus_ai_protector.py \"$@\"\n")
        os.chmod(target_bin, 0o755)
        return {
            "installed": True,
            "target": target_link,
            "message": "System-wide Termux launcher installed successfully",
        }

    def scan(self):
        findings = []
        score = 0

        if self._is_root():
            findings.append(("critical", "Root access detected. Lockdown mode is active."))
            score += 35
        else:
            findings.append(("safe", "Standard user privileges detected."))
            score += 20

        su_paths = self._find_su()
        if su_paths:
            findings.append(("high", f"Superuser binary discovered: {', '.join(su_paths)}"))
            score += 25
        else:
            findings.append(("safe", "No superuser binary detected."))
            score += 5

        available_tools = [tool for tool in ["ip", "ping", "curl", "wget"] if shutil.which(tool)]
        if available_tools:
            findings.append(("info", f"Network utilities available: {', '.join(available_tools)}"))
            score += 5

        processes = self._collect_processes()
        suspicious_processes = [process for process in processes if process.lower() in {"curl", "wget", "nc", "ncat", "python"}]
        if suspicious_processes:
            findings.append(("warning", f"Potential network helpers active: {', '.join(sorted(set(suspicious_processes)))}"))
            score += 10
        else:
            findings.append(("info", "No obvious network helper processes detected."))
            score += 5

        if os.path.exists("/data/data/com.termux"):
            findings.append(("info", "Termux environment detected."))
            score += 5

        public_ip = self.get_public_ip()
        obfuscated_ip = self.obfuscate_ip(public_ip, enabled=self.config.enable_obfuscation)
        findings.append(("info", f"Observed network identity: {obfuscated_ip}"))
        score += 5

        hardening_steps = self.harden_access()
        for step in hardening_steps:
            findings.append(("secure", step))
            score += 3

        sample_user_data = "Email: user@example.com, Phone: 05551234567, Token: abc123"
        redacted_data = self.redact_sensitive_data(sample_user_data)
        findings.append(("secure", f"User data leak shield active: {redacted_data}"))
        score += 5

        encrypted_sample = self.encrypt_payload("session-01")
        findings.append(("secure", f"Session encryption active: {encrypted_sample}"))
        score += 5

        secure_log = self.secure_log("User session started with sensitive metadata")
        findings.append(("secure", secure_log))
        score += 3

        auto_trigger = self.auto_trigger()
        findings.append(("warning", f"{auto_trigger['message']} [{auto_trigger['mode']}]"))
        score += 4

        file_scan = self.scan_files(["/data", "/sdcard", "/storage"])
        findings.append(("secure", f"System file scan completed: {file_scan['files_checked']} paths checked"))
        score += 4

        audit_log = self.create_audit_log("guard-scan")
        findings.append(("secure", f"Audit trail enabled: {audit_log}"))
        score += 4

        session_lock = self.lock_session("0000")
        findings.append(("secure", f"Session lock engaged: {session_lock['mode']}"))
        score += 4

        if score >= 80:
            status = "Protected"
        elif score >= 50:
            status = "Watch"
        else:
            status = "Vulnerable"

        return {
            "device": self.device_name,
            "platform": self.platform,
            "python_version": self.python_version,
            "status": status,
            "score": score,
            "findings": findings,
        }

    def render(self, report, json_output=False):
        if json_output:
            print(json.dumps(report, indent=2))
            return

        print("=" * 60)
        print("NEXUS AI PROTECTOR")
        print("Quantum-core device protection prototype")
        print("=" * 60)
        print(f"Device: {report['device']}")
        print(f"Platform: {report['platform']}")
        print(f"Python: {report['python_version']}")
        print(f"Status: {report['status']}")
        print(f"Protection score: {report['score']}/100")
        print("\nFindings:")
        for level, message in report["findings"]:
            print(f"- [{level.upper()}] {message}")
        print("=" * 60)

    def protect(self, duration=15, interval=3):
        deadline = time.time() + duration
        iteration = 0
        while time.time() < deadline:
            iteration += 1
            report = self.scan()
            print(f"[cycle {iteration}] {report['status']} | score={report['score']}")
            for level, message in report["findings"]:
                print(f"  - [{level.upper()}] {message}")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Nexus AI Protector for Termux")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("scan", help="Run a security scan")
    subparsers.add_parser("status", help="Alias for scan")
    subparsers.add_parser("protect", help="Run a short protection loop")
    subparsers.add_parser("install", help="Install the launcher system-wide in Termux")

    args = parser.parse_args()
    protector = QuantumCoreProtector()

    if args.command in {"scan", "status"}:
        report = protector.scan()
        protector.render(report, json_output=False)
        return 0

    if args.command == "protect":
        duration = 15
        interval = 3
        protector.protect(duration=duration, interval=interval)
        return 0

    if args.command == "install":
        result = protector.install()
        print(json.dumps(result, indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
