from mpplugs.Logger import *
from mpplugs.Settings import Settings
from mpplugs.Namespace import Namespace
from mpplugs.Event import PluginEvent

class Plugin(LogIssuer):
  def __init__(self, key):
    self.__mpplugs__ = Namespace(key=key, tick=0)
    self.setIssuerData('plugin', key)

  def init(self):
    pass

  def update(self):
    self.__mpplugs__.tick += 1

  def quit(self):
    Info(self, f'Plugin {self.__mpplugs__.key} quits')

  def __repr__(self):
    return f'<Plugin {self.__mpplugs__.key}>'

  # Stock events

  def addInputNode(self, key, handler, *paramKeys):
    node = Namespace(owner=self.__mpplugs__.key, key=key, paramKeys=list(paramKeys),
      handler=handler)
    self.executor.inputNodes[key] = node
    self.addEventHandler(f'$_{self.__mpplugs__.key}_{key}', handler)

  def addEventHandler(self, eventKey, handler):
    try: self.executor.evntHandlers[eventKey] += [handler]
    except: self.executor.evntHandlers[eventKey] = [handler]
    PluginEvent(self, 'AddHandler', eventKey=eventKey, plugin=self.__mpplugs__.key)

  def stopProgram(self):
    PluginEvent(self, 'StopProgram')

  def setPluginOutputs(self, **data):
    if Settings.Kernel.AutoAddTpsToPluginOutputs:
      data['TPS'] = self.executor.tpsMon.tps
    if Settings.Kernel.AutoAddTickToPluginOutputs:
      data['tick'] = self.__mpplugs__.tick
    PluginEvent(self, 'PluginStatus', pluginKey=self.__mpplugs__.key,
      data=Namespace(**data))
