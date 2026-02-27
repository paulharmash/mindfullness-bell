import unittest
from datetime import datetime, timedelta
from src import scheduler

class TestScheduler(unittest.TestCase):

    def test_get_next_ring_time(self):
        now = datetime.now()
        next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        
        # Calculate multiple times to ensure it stays within bounds
        for _ in range(50):
            next_time = scheduler.get_next_ring_time()
            
            # The next time must be within ±10 minutes of the next hour
            # (or the one after if it was in the past, but we just check the minute bounds)
            diff = abs((next_time - next_hour).total_seconds())
            
            # if next_time jumped to the hour after next hour
            if next_time >= next_hour + timedelta(hours=1, minutes=-10):
                diff = abs((next_time - (next_hour + timedelta(hours=1))).total_seconds())
                
            self.assertLessEqual(diff, 10 * 60)

if __name__ == '__main__':
    unittest.main()
