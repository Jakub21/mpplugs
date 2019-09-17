from datetime import datetime
from Pluginable.Namespace import Namespace

from colorama import init as cInit, Fore as cf
from colorama import Style as cs
cs.clr = cs.RESET_ALL
cInit()

class Logger:
  def __init__(self, file, mode):
    self.logger = Namespace()
    file = file.replace('\\', '/')
    self.logger.file = '::'.join(file.split('/')[-2:])[:-3]
    self.logger.mode = mode

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

  def logError(self, *msg):
    print(end=self._Time(cf.LIGHTRED_EX))
    print(end=f'[{cf.LIGHTRED_EX}{self.logger.file}{cs.clr}] ')
    print(f'{cf.LIGHTRED_EX}{" ".join(msg)}{cs.clr}')

  def logWarn(self, *msg):
    print(end=self._Time(cf.LIGHTBLACK_EX))
    print(end=f'[{cf.LIGHTYELLOW_EX}{self.logger.file}{cs.clr}] ')
    print(f'{cf.LIGHTYELLOW_EX}{" ".join(msg)}{cs.clr}')

  def logNote(self, *msg):
    print(end=self._Time(cf.LIGHTBLACK_EX))
    print(f'[{cf.LIGHTCYAN_EX}{self.logger.file}{cs.clr}] '+' '.join(msg))

  def logInfo(self, *msg):
    print(end=self._Time(cf.LIGHTBLACK_EX))
    print(f'[{self.logger.file}] '+' '.join(msg))

  def logDebug(self, *msg):
    print(end=self._Time(cf.LIGHTBLACK_EX))
    print(end=f'[{cf.LIGHTBLACK_EX}{self.logger.file}{cs.clr}] ')
    print(f'{cf.LIGHTBLACK_EX}{" ".join(msg)}{cs.clr}')
