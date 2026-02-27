import unittest
from unittest.mock import patch, mock_open
import json
import tempfile
from pathlib import Path
from src import config

class TestConfig(unittest.TestCase):

    @patch('src.config.CONFIG_FILE', Path(tempfile.gettempdir()) / "test_config.json")
    def test_load_config_defaults(self):
        # Ensure file doesn't exist
        if config.CONFIG_FILE.exists():
            config.CONFIG_FILE.unlink()
            
        c = config.load_config()
        self.assertEqual(c["volume"], config.DEFAULT_VOLUME)
        
    @patch('src.config.CONFIG_FILE', Path(tempfile.gettempdir()) / "test_config.json")
    def test_save_and_load_config(self):
        config.save_config({"volume": 0.8})
        c = config.load_config()
        self.assertEqual(c["volume"], 0.8)

    @patch('src.config.CONFIG_FILE', Path(tempfile.gettempdir()) / "test_config.json")
    def test_volume_bounds(self):
        # Save too high
        config.save_config({"volume": 1.5})
        self.assertEqual(config.load_config()["volume"], 1.0)
        
        # Save too low
        config.save_config({"volume": -0.5})
        self.assertEqual(config.load_config()["volume"], 0.0)
        
    @patch('src.config.CONFIG_FILE', Path(tempfile.gettempdir()) / "test_config.json")
    def test_corrupted_config(self):
        with open(config.CONFIG_FILE, 'w') as f:
            f.write("{ invalid json }")
        
        c = config.load_config()
        self.assertEqual(c["volume"], config.DEFAULT_VOLUME)

if __name__ == '__main__':
    unittest.main()
