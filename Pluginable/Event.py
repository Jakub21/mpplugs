from datetime import datetime

class Event:
  def __init__(self, key, **data):
    self.key = key
    self.when = datetime.now()
    self.__dict__.update(data)

  def __repr__(self):
    args = ', '.join([f'{k}={v}' for k, v in self.__dict__.items() if k not in ['key', 'when']])
    return f'<Event "{self.key}" {self.when.strftime("%H:%M:%S")} {{{args}}}>'
