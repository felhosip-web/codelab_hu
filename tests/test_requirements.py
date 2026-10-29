import os
import unittest


class TestRequirementsPinning(unittest.TestCase):
    def test_requirements_file_exists_and_pinned(self):
        req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        self.assertTrue(os.path.exists(req_path), "requirements.txt file should exist")

        with open(req_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        self.assertGreater(len(lines), 0, "requirements.txt should not be empty")

        for line in lines:
            self.assertIn("==", line, f"Requirement '{line}' in requirements.txt must be explicitly pinned with '=='")


if __name__ == "__main__":
    unittest.main()
