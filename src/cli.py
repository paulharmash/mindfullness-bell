import argparse
import sys
from . import daemon
from . import config
from . import scheduler
import subprocess
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Mindfulness Bell - A silent, resonant hourly companion.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: start
    parser_start = subparsers.add_parser("start", help="Starts the background daemon.")
    
    # Command: run
    parser_run = subparsers.add_parser("run", help="Runs the application in the foreground (used by launchd).")

    # Command: stop
    parser_stop = subparsers.add_parser("stop", help="Stops the background daemon.")
    
    # Command: autostart
    parser_autostart = subparsers.add_parser("autostart", help="Enables auto-start on macOS login using launchd.")

    # Command: disable-autostart
    parser_disable_autostart = subparsers.add_parser("disable-autostart", help="Disables auto-start on macOS login.")
    
    # Command: status
    parser_status = subparsers.add_parser("status", help="Prints current status and configuration.")
    
    # Command: volume
    parser_volume = subparsers.add_parser("volume", help="Sets the playback volume (0.0 to 1.0).")
    parser_volume.add_argument("level", type=float, help="Volume level from 0.0 to 1.0")

    args = parser.parse_args()

    if args.command == "start":
        daemon.start()
        print("Mindfulness Bell started.")

    elif args.command == "run":
        print("Running Mindfulness Bell in the foreground...")
        scheduler.run_scheduler_loop()

    elif args.command == "autostart":
        enable_autostart()

    elif args.command == "disable-autostart":
        disable_autostart()
        
    elif args.command == "stop":
        daemon.stop()
        
    elif args.command == "status":
        daemon.status()
        vol = config.get_volume()
        print(f"Current volume: {vol}")
        
    elif args.command == "volume":
        if 0.0 <= args.level <= 1.0:
            config.set_volume(args.level)
            print(f"Volume set to {args.level}")
        else:
            print("Volume must be between 0.0 and 1.0", file=sys.stderr)
            sys.exit(1)
            
    else:
        parser.print_help()

def get_plist_path():
    return Path.home() / "Library" / "LaunchAgents" / "com.mindfulness-bell.plist"

def enable_autostart():
    plist_path = get_plist_path()
    executable_path = Path(sys.argv[0]).resolve()
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mindfulness-bell</string>
    <key>ProgramArguments</key>
    <array>
        <string>{executable_path}</string>
        <string>run</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/mindfulness-bell.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mindfulness-bell.err.log</string>
</dict>
</plist>
"""
    
    # Write plist
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plist_path, "w") as f:
        f.write(plist_content)
        
    print(f"Created launchd plist at {plist_path}")
    
    # Load with launchctl
    try:
        # Unload first just in case
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        # Load
        subprocess.run(["launchctl", "load", str(plist_path)], check=True)
        print("Successfully enabled auto-start for Mindfulness Bell.")
        print("Note: The background app is now managed by macOS launchd. Use 'mindfulness-bell disable-autostart' to stop it.")
        
        # We should probably stop the old fashioned daemon so they don't conflict
        daemon.stop()
    except subprocess.CalledProcessError as e:
        print(f"Failed to load launchd agent: {e}", file=sys.stderr)

def disable_autostart():
    plist_path = get_plist_path()
    
    if plist_path.exists():
        try:
            subprocess.run(["launchctl", "unload", str(plist_path)], check=True)
            print("Unloaded launchd agent.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to unload launchd agent: {e}", file=sys.stderr)
            
        try:
            plist_path.unlink()
            print(f"Removed launchd plist at {plist_path}")
            print("Successfully disabled auto-start.")
        except OSError as e:
            print(f"Warning: Failed to remove plist: {e}", file=sys.stderr)
    else:
        print("Auto-start is not enabled (plist not found).")

if __name__ == "__main__":
    main()
