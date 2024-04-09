import time


class TimerManager:
    def __init__(self):
        self.timers = {}

    def create_timer(self, timer_id, timeout_seconds, callback_function):
        self.timers[timer_id] = (time.time(), timeout_seconds, callback_function)

    def check_timers(self):
        current_time = time.time()
        timers_to_delete = []
        for timer_id, (start_time, timeout_seconds, callback_function) in self.timers.items():
            if current_time - start_time >= timeout_seconds:
                callback_function(timer_id)

        for timer_id in timers_to_delete:
            del self.timers[timer_id]

    def cancel_timer(self, timer_id):
        if timer_id in self.timers:
            del self.timers[timer_id]

