import subprocess
import os
import sys
from pathlib import Path
from . import config
from typing import Optional

# Note: In a real distribution, we might use pkg_resources or resources
# to find the asset, but for this CLI structure, we'll locate it relative to this file
# or in a fixed standard location. Let's assume an 'assets' dir in the project root.
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_BELL_SOUND = PROJECT_ROOT / "assets" / "668646__tec_studio__temple-bell-001.wav"

def play_bell(sound_path: Path = DEFAULT_BELL_SOUND, override_volume: Optional[float] = None):
    """
    Plays the bell sound using the macOS `afplay` command.
    Checks config for volume if override is not provided.
    """
    if not sound_path.exists():
        print(f"Error: Bell sound file not found at {sound_path}", file=sys.stderr)
        # We don't exit entirely in case this was just a missing file but 
        # we want the daemon to keep running and recover later if placed back.
        return False
        
    volume = override_volume if override_volume is not None else config.get_volume()
    # macOS afplay volume ranges linearly. Technically afplay -v takes 0 to 255. 
    # Usually 1 is normal, >1 is amplified, <1 is attenuated. Let's scale 0.0-1.0 
    # directly as 0 to 1 which afplay interprets as 0 (silent) to 1 (full file volume).
    
    try:
        # afplay -v <volume> <file>
        # e.g., afplay -v 0.4 bell.wav
        # We use run and don't check output. We wait for it to finish.
        subprocess.run(
            ["afplay", "-v", str(volume), str(sound_path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        print("Error: `afplay` command not found on this system. Are you running macOS?", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error playing sound: {e}", file=sys.stderr)
        return False
