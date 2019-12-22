from Pluginable.Logger import *
from Pluginable.Namespace import Namespace
from Pluginable.Event import PluginEvent
from traceback import format_tb

class Plugin(LogIssuer):
  def __init__(self, key):
    self.key = key
    self.setIssuerData('plugin', self.key)
    self.tick = 0

  def addToStatus(self, attr):
    self.statusAttrs += [attr]

  def init(self):
    pass

  def update(self):
    self.tick += 1

  def quit(self):
    Info(self, f'Plugin {self.key} quits')

  def __repr__(self):
    return f'<Plugin {self.key}>'

  # Stock events

  def addInputNode(self, key, handler, *paramKeys):
    node = Namespace(owner=self.key, key=key, paramKeys=list(paramKeys),
      handler=handler)
    self.executor.inputNodes[key] = node
    self.executor.evntHandlers[f'$_{self.key}_{key}'] = [handler]

  def addEventHandler(self, eventKey, handler):
    try: self.executor.evntHandlers[eventKey] += [handler]
    except: self.executor.evntHandlers[eventKey] = [handler]
    PluginEvent(self, 'AddHandler', eventKey=eventKey, plugin=self.key)

  def stopProgram(self):
    PluginEvent(self, 'StopProgram')

  def raiseError(self, id, exception, critical=False, message=None):
    name = exception.__class__.__name__
    info = exception.args[0]
    traceback = ''.join(format_tb(exception.__traceback__))
    PluginEvent(self, 'PluginError', critical=critical, message=message,
      name=name, info=info, traceback=traceback)

  def setPluginOutputs(self, **data):
    PluginEvent(self, 'PluginStatus', pluginKey=self.key, tick=self.tick,
      data=Namespace(**data))
