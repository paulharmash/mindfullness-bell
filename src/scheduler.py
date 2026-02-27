import time
import random
from datetime import datetime, timedelta
import logging
from . import sys_state
from . import player

# Setup basic logging for debugging (to a file in config later, or syslog)
logger = logging.getLogger(__name__)

def get_next_ring_time() -> datetime:
    """
    Calculates the next time the bell should ring.
    It happens at the top of the upcoming hour, plus or minus a random
    offset of up to 10 minutes.
    """
    now = datetime.now()
    # Find the top of the next hour
    next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    
    # Random offset between -10 and +10 minutes
    # Using random.uniform for a fractional minute, or randint for seconds
    offset_seconds = random.randint(-10 * 60, 10 * 60)
    
    scheduled_time = next_hour + timedelta(seconds=offset_seconds)
    
    # If by some rare edge case the scheduled time is mostly in the past 
    # (e.g., if started at 13:58 and scheduled time is 13:55),
    # we just generate for the subsequent hour.
    if scheduled_time <= now:
        next_hour += timedelta(hours=1)
        scheduled_time = next_hour + timedelta(seconds=offset_seconds)
        
    return scheduled_time

def run_scheduler_loop():
    """
    The main infinite loop for the background daemon.
    Calculates next ring time, sleeps until then, checks conditions, rings, repeats.
    """
    while True:
        try:
            next_time = get_next_ring_time()
            now = datetime.now()
            
            sleep_duration = (next_time - now).total_seconds()
            logger.info(f"Scheduling next ring at {next_time.strftime('%Y-%m-%d %H:%M:%S')}. Sleeping for {sleep_duration:.1f} seconds.")
            
            # Using time.sleep is CPU efficient. The OS will wake the process up.
            # However, if the system sleeps and wakes up *after* `next_time`, 
            # sleep() might return immediately upon wake.
            time.sleep(max(0.0, sleep_duration))
            
            # Woke up at (or after) scheduled time.
            # Check if we should play
            if sys_state.should_play():
                logger.info("System state appropriate. Playing bell.")
                player.play_bell()
            else:
                logger.info("System state inappropriate (locked/sleeping/closed lid). Skipping ring.")
                
            # If the system slept and woke up way past the next_time, 
            # the loop will simply re-evaluate the *next* hour immediately in the next iteration.
            
        except KeyboardInterrupt:
            # Expected if running in foreground and stopped
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
            # Prevent rapid failure loops
            time.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_scheduler_loop()
