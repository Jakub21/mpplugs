from datetime import datetime
from Pluginable.Namespace import Namespace

from colorama import init as cInit, Fore as cf
from colorama import Style as cs
cs.clr = cs.RESET_ALL
cInit()

class Logger:
  def __init__(self, id, mode):
    self.logger = Namespace()
    self.logger.id = '::'.join(id)
    self.logger.brackets = {
      'pluginable': ('{', '}'),
      'plugin': ('[', ']'),
      'task': ('(', ')'),
    }[mode]

  def _Time(self, color):
    time = datetime.now()
    hour = str(time.hour)
    if len(hour) <2: hour = f'0{hour}'
    minute = str(time.minute)
    if len(minute) <2: minute = f'0{minute}'
    second = str(time.second)
    if len(second) <2: second = f'0{second}'
    time = f'{hour}:{minute}:{second}'
    return f'[{color}{time}{cs.clr}] '

  def _Log(self, timeColor, idColor, msgColor, *msg):
    o, c = self.logger.brackets
    print(end=self._Time(timeColor))
    print(end=f'{o}{idColor}{self.logger.id}{cs.clr}{c} ')
    print(f'{msgColor}{" ".join(msg)}{cs.clr}')

  def logError(self, *msg):
    self._Log(cf.LIGHTRED_EX, cf.LIGHTRED_EX, cf.LIGHTRED_EX, *msg)

  def logWarn(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.LIGHTYELLOW_EX, cf.LIGHTYELLOW_EX, *msg)

  def logNote(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.LIGHTCYAN_EX, cf.LIGHTBLACK_EX, *msg)

  def logInfo(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.WHITE, cf.WHITE, *msg)

  def logDebug(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.LIGHTBLACK_EX, cf.LIGHTBLACK_EX, *msg)
