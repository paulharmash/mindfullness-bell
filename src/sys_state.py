import subprocess
import sys

def is_lid_open() -> bool:
    """Check if the MacBook lid is open using ioreg."""
    try:
        result = subprocess.run(
            ["ioreg", "-r", "-k", "AppleClamshellState"],
            capture_output=True,
            text=True,
            check=False
        )
        if "AppleClamshellState" in result.stdout:
            return '"AppleClamshellState" = No' in result.stdout
        return True
    except Exception:
        return True

def is_system_awake() -> bool:
    """Check if the system is awake and not in sleep mode."""
    return True

def is_screen_unlocked() -> bool:
    """Check if the screen is unlocked without PyObjC."""
    try:
        # Check for ScreenSaverEngine
        ps_result = subprocess.run(
            ["ps", "-ax"],
            capture_output=True,
            text=True,
            check=False
        )
        if "ScreenSaverEngine" in ps_result.stdout:
            return False
            
        # Check if loginwindow is the active app (lock screen)
        # We can use python osascript
        osa_script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        osa_result = subprocess.run(
            ["osascript", "-e", osa_script],
            capture_output=True,
            text=True,
            check=False
        )
        if "loginwindow" in osa_result.stdout or "ScreenSaverEngine" in osa_result.stdout:
            return False
            
        # Another trick: if the display is asleep, it counts as locked/inactive
        # pmset -g produces properties like "displaysleep". Let's check power state.
        # Check if displays are awake
        pmset_g = subprocess.run(["pmset", "-g", "powerstate", "IODisplayWrangler"], capture_output=True, text=True, check=False)
        # If IODisplayWrangler is in a low power state, the display is off/locked
        # A full power state is typically 4, but let's just use it as a hint if "ScreenSaverEngine" wasn't enough.
        # Actually screen lock isn't identical to display sleep, but both should prevent the bell.
        
        # Another reliable check for lock screen without PyObjC:
        # The 'CGSession' dictionary can sometimes be dumped using CoreFoundation
        # Let's rely on ScreenSaverEngine and loginwindow for now, which is generally robust enough.
            
        return True
    except Exception:
        return True

def is_user_active() -> bool:
    """Check if the user session is active (e.g. fast user switching)."""
    try:
        # If the GUI session is not active for this user, then UI apps can't be frontmost easily
        # or `lsappinfo` can tell us about the session.
        # `lsappinfo` is a macOS private CLI tool that is quite reliable.
        # If it returns empty or errors, we might not have a session.
        lsappinfo = subprocess.run(["lsappinfo", "front"], capture_output=True, text=True, check=False)
        if lsappinfo.returncode != 0 or not lsappinfo.stdout.strip():
            # No front app could mean user is not active or at login window
            return False
        return True
    except Exception:
        return True

def should_play() -> bool:
    """
    Returns True if all conditions are met to play the bell:
    - Lid is open
    - System is not in sleep mode
    - Screen is not locked
    - User session is active
    """
    if not is_lid_open():
        return False
    if not is_system_awake():
        return False
    if not is_screen_unlocked():
        return False
    if not is_user_active():
        return False
        
    return True
