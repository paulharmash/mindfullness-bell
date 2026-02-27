import json
import os
from pathlib import Path

# The default volume (0.0 to 1.0)
DEFAULT_VOLUME = 0.4
CONFIG_DIR = Path.home() / ".config" / "mindfulness-bell"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_dir() -> Path:
    """Ensure config directory exists and return its path."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    """Load configuration from config file. Returns defaults if file doesn't exist."""
    if not CONFIG_FILE.exists():
        return save_config({"volume": DEFAULT_VOLUME})

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Ensure volume is always present and valid
            if "volume" not in config or not isinstance(config["volume"], (int, float)):
                config["volume"] = DEFAULT_VOLUME
            else:
                config["volume"] = max(0.0, min(1.0, float(config["volume"])))
            return config
    except (json.JSONDecodeError, OSError):
        # On corruption or read error, fallback to defaults
        return {"volume": DEFAULT_VOLUME}


def save_config(config: dict) -> dict:
    """Save configuration to config file."""
    # Enforce constraints
    volume = config.get("volume", DEFAULT_VOLUME)
    volume = max(0.0, min(1.0, float(volume)))
    config_to_save = {"volume": volume}
    
    get_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_to_save, f, indent=4)
    
    return config_to_save


def get_volume() -> float:
    """Convenience method to just get the volume."""
    return load_config()["volume"]


def set_volume(volume: float) -> None:
    """Convenience method to update just the volume."""
    config = load_config()
    config["volume"] = volume
    save_config(config)
