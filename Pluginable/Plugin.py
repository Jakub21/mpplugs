from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace
from Pluginable.Event import PluginEvent

class Plugin(Logger):
  def __init__(self, key, logLock):
    self.key = key
    super().__init__(self.key, 'plugin', logLock)
    self.tick = 0

  def init(self):
    self.INITIALIZED = True

  def update(self):
    self.tick += 1

  def quit(self):
    self.logInfo(f'Plugin {self.key} quits')

  def __repr__(self):
    return f'<Plugin {self.key}>'

  # Stock events

  def addEventHandler(self, eventKey, handler):
    try: self.executor.evntHandlers[eventKey] += [handler]
    except: self.executor.evntHandlers[eventKey] = [handler]
    PluginEvent(self, 'AddHandler', eventKey=eventKey, plugin=self.key)

  def stopProgram(self):
    PluginEvent(self, 'StopProgram')

  def RaiseError(self, id, exception=None, message=None, severity=0):
    PluginEvent(self, 'PluginError', exception=exception, message=message,
      severity=severity)
