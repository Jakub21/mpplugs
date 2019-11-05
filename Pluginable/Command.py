from datetime import datetime

class Command:
  def __init__(self, what, **data):
    self.what = what
    self.__dict__.update(data)

  def getArgs(self):
    return {k:v for k, v in self.__dict__.items() if k != 'what'}
