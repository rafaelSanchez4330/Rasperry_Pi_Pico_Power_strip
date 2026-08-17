import unittest

import _bootstrap  # noqa: F401  (configura sys.path)

from outlets import Outlet, OutletManager


class OutletTests(unittest.TestCase):
    def test_starts_off(self):
        outlet = Outlet(1, "Test", 2, active_low=True, default_on=False)
        self.assertFalse(outlet.is_on())

    def test_turn_on_off_toggle(self):
        outlet = Outlet(1, "Test", 2, active_low=True)
        outlet.turn_on()
        self.assertTrue(outlet.is_on())
        outlet.turn_off()
        self.assertFalse(outlet.is_on())
        self.assertTrue(outlet.toggle())
        self.assertFalse(outlet.toggle())

    def test_active_low_pin_level(self):
        outlet = Outlet(1, "Test", 2, active_low=True)
        outlet.turn_on()
        self.assertEqual(outlet._pin.value(), 0)  # active-low: ON == LOW
        outlet.turn_off()
        self.assertEqual(outlet._pin.value(), 1)

    def test_active_high_pin_level(self):
        outlet = Outlet(1, "Test", 2, active_low=False)
        outlet.turn_on()
        self.assertEqual(outlet._pin.value(), 1)
        outlet.turn_off()
        self.assertEqual(outlet._pin.value(), 0)

    def test_to_dict(self):
        outlet = Outlet(3, "Monitor", 4, active_low=True)
        outlet.turn_on()
        self.assertEqual(
            outlet.to_dict(),
            {"id": 3, "name": "Monitor", "gpio": 4, "state": "on"},
        )


class OutletManagerTests(unittest.TestCase):
    def _manager(self):
        return OutletManager.from_config()

    def test_from_config_creates_six(self):
        manager = self._manager()
        self.assertEqual(len(manager.all()), 6)

    def test_get_by_id(self):
        manager = self._manager()
        self.assertIsNotNone(manager.get(1))
        self.assertIsNone(manager.get(99))

    def test_all_on_off(self):
        manager = self._manager()
        manager.all_on()
        self.assertTrue(all(o.is_on() for o in manager.all()))
        manager.all_off()
        self.assertTrue(all(not o.is_on() for o in manager.all()))

    def test_to_dict_shape(self):
        manager = self._manager()
        payload = manager.to_dict()
        self.assertIn("outlets", payload)
        self.assertEqual(len(payload["outlets"]), 6)


if __name__ == "__main__":
    unittest.main()
