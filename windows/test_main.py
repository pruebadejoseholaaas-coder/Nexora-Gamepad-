import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import main


class ProtocolTests(unittest.TestCase):
    def test_clamp_limits_values(self):
        self.assertEqual(main.clamp(2, -1, 1), 1)
        self.assertEqual(main.clamp(-2, -1, 1), -1)
        self.assertEqual(main.clamp("invalid", 0, 1), 0)
        self.assertEqual(main.clamp(float("nan"), -1, 1), 0)
        self.assertEqual(main.clamp(float("inf"), -1, 1), 0)

    def test_accepts_valid_input(self):
        parsed = main.parse_input({
            "type": "input",
            "version": 1,
            "buttons": ["A", "LB", "UNKNOWN"],
            "axes": {"leftX": 0.5, "leftY": -0.25},
        })
        self.assertIsNotNone(parsed)
        buttons, axes = parsed
        self.assertEqual(buttons, {"A", "LB"})
        self.assertEqual(axes["leftX"], 0.5)

    def test_rejects_wrong_message_type_and_version(self):
        self.assertIsNone(main.parse_input({"type": "hello", "version": 1}))
        self.assertIsNone(main.parse_input({"type": "input", "version": 9}))

    def test_rejects_invalid_containers(self):
        self.assertIsNone(main.parse_input({"type": "input", "version": 1, "buttons": "A"}))
        self.assertIsNone(main.parse_input({"type": "input", "version": 1, "axes": []}))


if __name__ == "__main__":
    unittest.main()
