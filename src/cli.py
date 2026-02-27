import argparse
import sys
from src import daemon
from src import config

def main():
    parser = argparse.ArgumentParser(description="Mindfulness Bell - A silent, resonant hourly companion.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: start
    parser_start = subparsers.add_parser("start", help="Starts the background daemon.")
    
    # Command: stop
    parser_stop = subparsers.add_parser("stop", help="Stops the background daemon.")
    
    # Command: status
    parser_status = subparsers.add_parser("status", help="Prints current status and configuration.")
    
    # Command: volume
    parser_volume = subparsers.add_parser("volume", help="Sets the playback volume (0.0 to 1.0).")
    parser_volume.add_argument("level", type=float, help="Volume level from 0.0 to 1.0")

    args = parser.parse_args()

    if args.command == "start":
        daemon.start()
        print("Mindfulness Bell started.")
        
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

if __name__ == "__main__":
    main()
