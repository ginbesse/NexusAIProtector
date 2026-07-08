import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import nexus_ai_protector as protector_module


class ProtectorTests(unittest.TestCase):
    def test_scan_returns_report(self):
        p = protector_module.QuantumCoreProtector()
        report = p.scan()
        self.assertIn("status", report)
        self.assertIn("score", report)
        self.assertIn("findings", report)

    def test_obfuscate_ip_uses_localhost_when_disabled(self):
        p = protector_module.QuantumCoreProtector()
        result = p.obfuscate_ip("127.0.0.1", enabled=False)
        self.assertEqual(result, "127.0.0.1")

    def test_obfuscate_ip_masks_address_when_enabled(self):
        p = protector_module.QuantumCoreProtector()
        result = p.obfuscate_ip("8.8.8.8", enabled=True)
        self.assertIn("***", result)

    def test_redact_sensitive_data_masks_private_fields(self):
        p = protector_module.QuantumCoreProtector()
        text = "Email: user@example.com, Phone: 05551234567, Token: abc123"
        result = p.redact_sensitive_data(text)
        self.assertNotIn("user@example.com", result)
        self.assertNotIn("05551234567", result)
        self.assertNotIn("abc123", result)
        self.assertIn("[REDACTED]", result)


if __name__ == "__main__":
    unittest.main()
