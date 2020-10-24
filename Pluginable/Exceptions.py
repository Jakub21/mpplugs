from Pluginable.Namespace import Namespace
from traceback import format_tb

class PluginableException(Exception):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.name = self.__class__.__name__
    self.info = self.args[0]

# Compiler

class CompilerError(PluginableException):
  pass

class CompilerNoDirectoryError(CompilerError):
  def __init__(self, path):
    super().__init__(f'Plugins directory added to config does not exist ({path})')

class CompilerNoDirsAddedError(CompilerError):
  def __init__(self):
    super().__init__(f'No plugin directories were added to compiler config')

class CompilerMissingFileError(CompilerError):
  def __init__(self, path):
    super().__init__(f'Missing required plugin file ({path})')

class CompilerMissingClassError(CompilerError):
  def __init__(self, pluginKey, className):
    super().__init__(f'Failed to find class "{className}" in plugin {pluginKey}')


# Plugin

class PluginError(PluginableException):
  def __init__(self, pluginData, original, message, lineNo=None, msg=None,
      offset=None, lineCode=None, includeLocation=True, includeFunction=True,
      includeOrig=False):
    formatDict = pluginData.__dict__
    # Parsing traceback
    traceback = ''.join(format_tb(original.__traceback__))
    self.originalTraceback = traceback
    tracebackFileLines = [l for l in traceback.split('\n') if '  File "' in l]
    locationLine = [l for l in traceback.split('\n') if '  File "' in l][-1]
    fullFilePath = locationLine.split('"')[1]
    # Getting original function name from TB
    functionName = locationLine.replace(fullFilePath, '').split()[5]
    formatDict['functionName'] = functionName
    # Getting original line number from TB
    if lineNo is None:
      lineNo = int(locationLine.replace(fullFilePath, '').split()[3][:-1])
    # Getting original message from TB
    if msg is None:
      msg = original.__class__.__name__ + ': ' + str(original.args)
    formatDict['origMssg'] = msg
    formatDict['origName'] = original.__class__.__name__
    formatDict['origArgs'] = " | ".join([str(x) for x in original.args])
    # Finding real file name and line number
    line = lineNo
    filesData = pluginData.sourceFileLines
    for name, amount in filesData:
      if line <= amount: formatDict['filename'] = name; break
      line -= amount
    formatDict['line'] = line
    # Append standard exception info
    info = message.format(**formatDict)
    try:
      if includeLocation:
        info += ('\n  File "{directory}/{key}/{filename}"' + \
        ', line {line}').format(**formatDict)
    except KeyError: pass
    try:
      if includeFunction:
        info += ', in {functionName}'.format(**formatDict)
    except KeyError: pass
    try:
      if includeOrig:
        info += '\n  {origName}: {origArgs}'.format(**formatDict)
    except KeyError: pass
    # Done
    super().__init__(info)

class PluginStartupError(PluginError): pass

class PluginSyntaxError(PluginStartupError):
  def __init__(self, pluginData, original):
    message = 'There is a syntax error in plugin {key}'
    original.args = (original.args[0])
    super().__init__(pluginData, original, message, lineNo=original.lineno,
      msg=original.msg, offset=original.offset, lineCode=original.text)

class PluginLoadError(PluginStartupError):
  def __init__(self, pluginData, original):
    message = 'Error occurred during load of plugin {key}'
    super().__init__(pluginData, original, message, includeOrig=True)

class PluginConfigError(PluginStartupError):
  def __init__(self, plugin, configPath, original):
    super().__init__(plugin, original,
      'Plugin {key}: config "'+configPath+'" does not exist')


# Plugin at Runtime

class PluginRuntimeError(PluginError): pass

class PluginInitError(PluginRuntimeError):
  def __init__(self, plugin, original):
    super().__init__(plugin.__pluginable__, original, \
      'An error occurred during init of plugin {key}', includeOrig=True)

class PluginTickError(PluginRuntimeError):
  def __init__(self, plugin, original):
    super().__init__(plugin.__pluginable__, original, \
      'An error occurred during {key} plugin tick', includeOrig=True)

class PluginEventError(PluginRuntimeError):
  def __init__(self, plugin, eventKey, original):
    super().__init__(plugin.__pluginable__, original, \
      'An error occurred in {key}\'s handler of event ' + eventKey,
      includeOrig=True)
