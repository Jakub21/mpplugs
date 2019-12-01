from Pluginable.Logger import *
from Pluginable.Namespace import Namespace
from Pluginable.Event import PluginEvent

class Plugin(LogIssuer):
  def __init__(self, key):
    self.key = key
    self.setIssuerData('plugin', self.key)
    self.tick = 0
    self.statusGetters = Namespace()

  def addToStatus(self, key, getter):
    self.statusGetters[key] = getter

  def init(self):
    self.INITIALIZED = True

  def update(self):
    self.tick += 1

  def quit(self):
    Info(self, f'Plugin {self.key} quits')

  def __repr__(self):
    return f'<Plugin {self.key}>'

  # Stock events

  def addEventHandler(self, eventKey, handler):
    try: self.executor.evntHandlers[eventKey] += [handler]
    except: self.executor.evntHandlers[eventKey] = [handler]
    PluginEvent(self, 'AddHandler', eventKey=eventKey, plugin=self.key)

  def stopProgram(self):
    PluginEvent(self, 'StopProgram')

  def raiseError(self, id, exception=None, message=None, severity=0):
    PluginEvent(self, 'PluginError', exception=exception, message=message,
      severity=severity)

  def pluginStatus(self):
    PluginEvent(self, 'PluginStatus', tick=self.tick,
      data=Namespace(**{k:v() for k, v in self.statusGetters.items()}))
