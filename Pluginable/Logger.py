from datetime import datetime
from Pluginable.Namespace import Namespace
from Pluginable.Settings import Settings
from Pluginable.LogColor import LogColor as CLR

class LogIssuer:
  def setIssuerData(self, issuerType, entPath):
    self._logger_data = Namespace(type=issuerType, path=entPath)

def _getTime():
  time = datetime.now()
  mode = Settings.Logger.timeMode
  if mode == 'relative':
    delta = time - Settings.StartTime
    time = str(delta)
    time = time[:time.index('.')+2]
  elif mode == 'absolute':
    if Settings.Logger.timeFormat == '12h': fs = '%p %I:%M:%S'
    elif Settings.Logger.timeFormat == '24h': fs = '%H:%M:%S'
    time = time.strftime(fs)
  return Settings.Logger.timePrefix[mode] + time

def _format(data, output, level, *message):
  message = ' '.join([str(elm) for elm in message])
  if level == 'error': message += '\n'
  time = _getTime()
  if not output.colored:
    return f'{time} <{data.type}:{data.path}> {message}\n'
  else:
    timeColor, prefixColor, msgColor = Settings.Logger.colors[level]
    timeColor = CLR.fg[timeColor]
    prefixColor, msgColor = CLR.fg[prefixColor], CLR.fg[msgColor]
    issuerType = Settings.Text.LogIssuerTypes[data.type]
    return f'{timeColor}{time}{CLR.rst} ' + \
      f'{prefixColor}<{issuerType}:{data.path}>{CLR.rst} ' + \
      f'{msgColor}{message}{CLR.rst}\n'

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
