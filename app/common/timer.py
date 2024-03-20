from apscheduler.schedulers.background import BackgroundScheduler
from libs.pyhelper.singleton import SingletonMeta


class Timer(metaclass=SingletonMeta):

    def __init__(self):
        self._id = 0
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def add_repeat_timer(self, func, seconds):
        self._id += 1
        self.scheduler.add_job(func, 'interval', seconds=seconds, id=self._id)
        return self._id

    def add_timer(self, func, seconds):
        self._id += 1
        self.scheduler.add_job(func, 'date', run_date=seconds, id=self._id)
        return self._id

    def remove_timer(self, timer_id):
        self.scheduler.remove_job(timer_id)
        return True
