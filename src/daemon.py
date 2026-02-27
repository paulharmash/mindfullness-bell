import os
import sys
import atexit
import signal
from pathlib import Path
from . import config
from . import scheduler

# Location for the PID file
PID_FILE = config.get_config_dir() / "mindfulness-bell.pid"

def daemonize():
    """
    Deamonize class. UNIX double fork mechanism.
    """
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"fork #1 failed: {e.errno} ({e.strerror})\n")
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"fork #2 failed: {e.errno} ({e.strerror})\n")
        sys.exit(1)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    
    # In python 3, we can just open /dev/null
    with open(os.devnull, 'r') as devnull:
        os.dup2(devnull.fileno(), sys.stdin.fileno())
    with open(os.devnull, 'a+') as devnull:
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())

    # write pidfile
    atexit.register(delpid)
    pid = str(os.getpid())
    with open(PID_FILE, 'w') as f:
        f.write(f"{pid}\n")
        
    # Start the actual work
    scheduler.run_scheduler_loop()

def delpid():
    if PID_FILE.exists():
        os.remove(PID_FILE)

def get_pid():
    if not PID_FILE.exists():
        return None
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        return pid
    except ValueError:
        return None

def start():
    """Start the daemon."""
    pid = get_pid()
    if pid:
        # Check if the process is actually running
        try:
            os.kill(pid, 0)
            print(f"Mindfulness Bell is already running (PID: {pid}).", file=sys.stderr)
            sys.exit(1)
        except OSError:
            # Stale PID file
            delpid()

    print("Starting Mindfulness Bell...")
    daemonize()

def stop():
    """Stop the daemon."""
    pid = get_pid()
    if not pid:
        print("Mindfulness Bell is not running (no PID file found).", file=sys.stderr)
        return

    # Try killing the daemon process
    try:
        while True:
            os.kill(pid, signal.SIGTERM)
            import time
            time.sleep(0.1)
    except OSError as err:
        err_str = str(err)
        if err_str.find("No such process") > 0:
            delpid()
            print("Mindfulness Bell stopped.")
        else:
            print(str(err), file=sys.stderr)
            sys.exit(1)

def status():
    """Check daemon status."""
    pid = get_pid()
    if pid:
        try:
            os.kill(pid, 0)
            print(f"Mindfulness Bell is running (PID: {pid}).")
            return
        except OSError:
            delpid()
            
    print("Mindfulness Bell is stopped.")
