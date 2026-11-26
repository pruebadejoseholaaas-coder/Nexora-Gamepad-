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

    def test_rumble_message_normalizes_motors_and_bounds_duration(self):
        message = main.build_rumble_message("123456", 255, 128, 900)
        self.assertEqual(message["type"], "rumble")
        self.assertEqual(message["version"], 1)
        self.assertEqual(message["code"], "123456")
        self.assertEqual(message["strength"], 1.0)
        self.assertEqual(message["durationMs"], 500)

    def test_rumble_message_handles_zero_and_invalid_motor_values(self):
        message = main.build_rumble_message("654321", 0, float("nan"), -5)
        self.assertEqual(message["strength"], 0.0)
        self.assertEqual(message["durationMs"], 0)

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


    def test_merge_clamps_untrusted_axis_values(self):
        states = {
            "phone": ({"A"}, {"leftX": 9, "leftY": float("nan"),
                              "leftTrigger": -4, "rightTrigger": 3}, 1.0)
        }
        buttons, axes = main.merge_client_states(states)
        self.assertEqual(buttons, {"A"})
        self.assertEqual(axes["leftX"], 1)
        self.assertEqual(axes["leftY"], 0)
        self.assertEqual(axes["leftTrigger"], 0)
        self.assertEqual(axes["rightTrigger"], 1)

    def test_merge_supports_four_phones_without_losing_buttons(self):
        states = {
            "phone1": ({"A"}, {"leftX": 0.2}, 1.0),
            "phone2": ({"B"}, {"leftX": -0.9}, 1.0),
            "phone3": ({"X"}, {"rightY": 0.6}, 1.0),
            "phone4": ({"Y", "START"}, {"rightY": -0.8}, 1.0),
        }
        buttons, axes = main.merge_client_states(states)
        self.assertEqual(buttons, {"A", "B", "X", "Y", "START"})
        self.assertEqual(axes["leftX"], -0.9)
        self.assertEqual(axes["rightY"], -0.8)

    def test_keyboard_trigger_uses_threshold(self):
        self.assertEqual(main.keyboard_keys(set(), {"leftTrigger": 0.6}), {0x31})
        self.assertEqual(main.keyboard_keys(set(), {"rightTrigger": 0.5}), set())

    def test_parse_input_ignores_unknown_axes(self):
        parsed = main.parse_input({
            "type": "input", "version": 1,
            "buttons": [], "axes": {"leftX": 0.4, "unexpected": 999}
        })
        self.assertEqual(parsed[1], {"leftX": 0.4})

    def test_expire_inactive_clients_removes_only_stale_phone(self):
        seen = {"old": 10.0, "active": 10.8}
        states = {
            "old": ({"A"}, {"leftX": 1.0}, 10.0),
            "active": ({"B"}, {"leftX": -1.0}, 10.8),
        }
        paired = {"old", "active"}
        expired = main.expire_inactive_clients(seen, states, paired, now=11.2, timeout=1.0)
        self.assertEqual(expired, ["old"])
        self.assertEqual(set(seen), {"active"})
        self.assertEqual(set(states), {"active"})
        self.assertEqual(paired, {"active"})

    def test_expire_inactive_clients_returns_empty_when_all_active(self):
        seen = {"phone": 20.0}
        states = {"phone": (set(), {}, 20.0)}
        paired = {"phone"}
        self.assertEqual(main.expire_inactive_clients(seen, states, paired, now=20.5), [])
        self.assertEqual(paired, {"phone"})


if __name__ == "__main__":
    unittest.main()
