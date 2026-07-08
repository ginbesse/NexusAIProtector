import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import nexus_ai_protector as protector_module


class ExtraFeaturesTests(unittest.TestCase):
    def test_encrypt_payload_returns_obfuscated_value(self):
        p = protector_module.QuantumCoreProtector()
        result = p.encrypt_payload("secret-session")
        self.assertIn(":", result)

    def test_protect_session_returns_status(self):
        p = protector_module.QuantumCoreProtector()
        result = p.protect_session("alpha")
        self.assertEqual(result["status"], "session-protected")

    def test_auto_trigger_returns_adapter_mode(self):
        p = protector_module.QuantumCoreProtector()
        result = p.auto_trigger()
        self.assertTrue(result["triggered"])
        self.assertIn("lock", result["mode"])

    def test_scan_files_detects_known_sensitive_paths(self):
        p = protector_module.QuantumCoreProtector()
        result = p.scan_files(["/tmp"])
        self.assertIn("files_checked", result)
        self.assertIn("findings", result)

    def test_create_audit_log_writes_file(self):
        p = protector_module.QuantumCoreProtector()
        log_path = p.create_audit_log("audit-test")
        self.assertTrue(Path(log_path).exists())

    def test_lock_session_returns_locked_state(self):
        p = protector_module.QuantumCoreProtector()
        result = p.lock_session("1234")
        self.assertEqual(result["state"], "locked")


if __name__ == "__main__":
    unittest.main()
