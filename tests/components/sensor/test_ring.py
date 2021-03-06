"""The tests for the Ring sensor platform."""
import unittest
import requests_mock

from homeassistant.components.sensor import ring
from homeassistant.components import ring as base_ring

from tests.components.test_ring import ATTRIBUTION, VALID_CONFIG
from tests.common import get_test_home_assistant, load_fixture


class TestRingSensorSetup(unittest.TestCase):
    """Test the Ring platform."""

    DEVICES = []

    def add_devices(self, devices, action):
        """Mock add devices."""
        for device in devices:
            self.DEVICES.append(device)

    def setUp(self):
        """Initialize values for this testcase class."""
        self.hass = get_test_home_assistant()
        self.config = {
            'username': 'foo',
            'password': 'bar',
            'monitored_conditions': [
                'battery',
                'last_activity',
                'last_ding',
                'last_motion',
                'volume']
        }

    def tearDown(self):
        """Stop everything that was started."""
        self.hass.stop()

    @requests_mock.Mocker()
    def test_sensor(self, mock):
        """Test the Ring senskor class and methods."""
        mock.post('https://api.ring.com/clients_api/session',
                  text=load_fixture('ring_session.json'))
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987652/history',
                 text=load_fixture('ring_doorbots.json'))
        base_ring.setup(self.hass, VALID_CONFIG)
        ring.setup_platform(self.hass,
                            self.config,
                            self.add_devices,
                            None)

        for device in self.DEVICES:
            device.update()
            if device.name == 'Front Door Battery':
                self.assertEqual(100, device.state)
                self.assertEqual('lpd_v1',
                                 device.device_state_attributes['kind'])
                self.assertNotEqual('chimes',
                                    device.device_state_attributes['type'])
            if device.name == 'Downstairs Volume':
                self.assertEqual(2, device.state)
                self.assertEqual('1.2.3',
                                 device.device_state_attributes['firmware'])
                self.assertEqual('mdi:bell-ring', device.icon)
                self.assertEqual('chimes',
                                 device.device_state_attributes['type'])
            if device.name == 'Front Door Last Activity':
                self.assertFalse(device.device_state_attributes['answered'])
                self.assertEqual('America/New_York',
                                 device.device_state_attributes['timezone'])

            self.assertIsNone(device.entity_picture)
            self.assertEqual(ATTRIBUTION,
                             device.device_state_attributes['attribution'])
