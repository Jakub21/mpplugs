from Pluginable.Logger import *
from Pluginable.Settings import Settings
from Pluginable.Namespace import Namespace
from Pluginable.Event import PluginEvent

class Plugin(LogIssuer):
  def __init__(self, key):
    self.__pluginable__ = Namespace(key=key, tick=0)
    self.setIssuerData('plugin', key)

  def init(self):
    pass

  def update(self):
    self.__pluginable__.tick += 1

  def quit(self):
    Info(self, f'Plugin {self.__pluginable__.key} quits')

  def __repr__(self):
    return f'<Plugin {self.__pluginable__.key}>'

  # Stock events

  def addInputNode(self, key, handler, *paramKeys):
    node = Namespace(owner=self.__pluginable__.key, key=key, paramKeys=list(paramKeys),
      handler=handler)
    self.executor.inputNodes[key] = node
    self.addEventHandler(f'$_{self.__pluginable__.key}_{key}', handler)

  def addEventHandler(self, eventKey, handler):
    try: self.executor.evntHandlers[eventKey] += [handler]
    except: self.executor.evntHandlers[eventKey] = [handler]
    PluginEvent(self, 'AddHandler', eventKey=eventKey, plugin=self.__pluginable__.key)

  def stopProgram(self):
    PluginEvent(self, 'StopProgram')

  def setPluginOutputs(self, **data):
    if Settings.Kernel.AutoAddTpsToPluginOutputs:
      data['TPS'] = self.executor.tpsMon.tps
    if Settings.Kernel.AutoAddTickToPluginOutputs:
      data['tick'] = self.__pluginable__.tick
    PluginEvent(self, 'PluginStatus', pluginKey=self.__pluginable__.key,
      data=Namespace(**data))
