from datetime import datetime
from Pluginable.Namespace import Namespace
from Pluginable.Settings import Settings

from colorama import init as coloramaInit
from colorama import Style as cs, Fore as cf
cs.clr = cs.RESET_ALL
print('-'*64, 'init colors', '-'*64, sep='\n')
coloramaInit(convert=True)

try: Settings.Logger.Start
except: Settings.Logger.Start = datetime.now()

class LogIssuer:
  def setIssuerData(self, issuerType, entPath):
    self._logger_data = Namespace(type=issuerType, path=entPath)
    coloramaInit()

def _getTime(color):
  time = datetime.now()
  if Settings.Logger.timeRelative:
    delta = time - Settings.Logger.Start
    time = str(delta)
  else:
    if Settings.Logger.timeFormat == '12h': fs = '%p %I:%M:%S'
    elif Settings.Logger.timeFormat == '24h': fs = '%H:%M:%S'
    time = time.strftime(fs)
  if color is not None: return f'{color}@{time}{cs.clr} '
  else: return '@' + time

def _format(data, output, level, *message):
  time = _getTime(cf.LIGHTMAGENTA_EX if output.colored else None)
  message = ' '.join(message)
  if not output.colored: return f'{time} <{data.type}:{data.path}> {message}\n'
  else:
    prefixColor, msgColor = Settings.Logger.colors[level]
    prefixColor = eval(f'cf.{prefixColor}')
    msgColor = eval(f'cf.{msgColor}')
    return f'{time} {prefixColor}<{data.type}:{data.path}>{cs.clr} ' + \
      f'{msgColor}{message}{cs.clr}\n'

def _addLog(entity, level, *message):
  try: data = entity._logger_data
  except AttributeError: data = Namespace(type='unknown', path='UNKNOWN')
  levelno = ['debug', 'info', 'note', 'warn', 'error'].index(level)
  for output in Settings.Logger.logOutputs:
    if levelno >= output.minLevel and levelno <= output.maxLevel:
      output.write(_format(data, output, level, *message))

def Debug(issuer, *message): _addLog(issuer, 'debug', *message)
def Info(issuer, *message): _addLog(issuer, 'info', *message)
def Note(issuer, *message): _addLog(issuer, 'note', *message)
def Warn(issuer, *message): _addLog(issuer, 'warn', *message)
def Error(issuer, *message): _addLog(issuer, 'error', *message)
