from datetime import datetime
from Pluginable.Namespace import Namespace
from Pluginable.Settings import Settings

from colorama import init as cInit, Fore as cf
from colorama import Style as cs
cs.clr = cs.RESET_ALL
cInit()

class Logger:
  def __init__(self, id, mode, lock):
    self.logger = Namespace()
    self.logger.lock = lock
    self.logger.id = id
    self.logger.mode = { 'pluginable': 'Kernel', 'plugin': 'Plugin'}[mode]

  def _Time(self, color):
    # TODO: In new logger include time relative to start of the program
    fs = '%p %I:%M:%S' if Settings.Logger.timeFormat == '12h' else '%H:%M:%S'
    return f'{color}@{datetime.now().strftime(fs)}{cs.clr} '

  def _Log(self, timeColor, idColor, msgColor, *msg):
    try: self.logger.lock.acquire()
    except FileNotFoundError: return
    text = self._Time(timeColor) + idColor
    text += f'<{self.logger.mode}::{self.logger.id}> '
    text += cs.clr + msgColor + ' '.join([str(m) for m in msg]) + cs.clr
    print(text)
    self.logger.lock.release()

  def logError(self, *msg):
    self._Log(cf.LIGHTRED_EX, cf.LIGHTRED_EX, cf.LIGHTRED_EX, *msg)

  def logWarn(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.LIGHTYELLOW_EX, cf.LIGHTYELLOW_EX, *msg)

  def logNote(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.LIGHTCYAN_EX, cf.WHITE, *msg)

  def logInfo(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.WHITE, cf.WHITE, *msg)

  def logDebug(self, *msg):
    self._Log(cf.LIGHTMAGENTA_EX, cf.LIGHTBLACK_EX, cf.LIGHTBLACK_EX, *msg)
