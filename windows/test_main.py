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

    def test_keyboard_fallback_maps_buttons_and_sticks(self):
        keys = main.keyboard_keys(
            {"A", "UP", "LB"},
            {"leftX": -0.8, "leftY": 0.0, "rightX": 0.7,
             "rightY": 0.0, "leftTrigger": 0.0, "rightTrigger": 0.9},
        )
        self.assertEqual(keys, {0x4A, 0x26, 0x51, 0x41, 0x48, 0x32})

    def test_keyboard_fallback_has_deadzone_threshold(self):
        keys = main.keyboard_keys(set(), {"leftX": 0.4, "leftY": -0.2})
        self.assertEqual(keys, set())

    def test_merge_client_states_combines_buttons_and_sticks(self):
        states = {
            "192.168.1.20": ({"A"}, {"leftX": 0.8, "leftY": 0.0}, 1.0),
            "192.168.1.21": ({"B"}, {"leftX": -0.4, "leftY": -0.7}, 1.1),
        }
        buttons, axes = main.merge_client_states(states)
        self.assertEqual(buttons, {"A", "B"})
        self.assertEqual(axes["leftX"], 0.8)
        self.assertEqual(axes["leftY"], -0.7)

    def test_merge_client_states_handles_no_phones(self):
        self.assertEqual(main.merge_client_states({}), (set(), {}))


if __name__ == "__main__":
    unittest.main()
