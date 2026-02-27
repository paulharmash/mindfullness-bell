import unittest
from unittest.mock import patch
from src import sys_state

class TestSysState(unittest.TestCase):

    @patch('subprocess.run')
    def test_is_lid_open_true(self, mock_run):
        mock_run.return_value.stdout = '"AppleClamshellState" = No'
        self.assertTrue(sys_state.is_lid_open())
        
    @patch('subprocess.run')
    def test_is_lid_open_false(self, mock_run):
        mock_run.return_value.stdout = '"AppleClamshellState" = Yes'
        self.assertFalse(sys_state.is_lid_open())
        
    @patch('subprocess.run')
    def test_is_screen_unlocked_locked_screensaver(self, mock_run):
        mock_run.return_value.stdout = '... ScreenSaverEngine ...'
        self.assertFalse(sys_state.is_screen_unlocked())

if __name__ == '__main__':
    unittest.main()
