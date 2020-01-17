from datetime import datetime
import multiprocessing as mpr
from Pluginable.Exceptions import *
from Pluginable.Settings import Settings
from Pluginable.Logger import *
from Pluginable.Namespace import Namespace
from Pluginable.Event import *
from Pluginable.TpsMonitor import TpsMonitor
import Pluginable.MultiHandler as mh

class Executor(LogIssuer):
  def __init__(self, plugin, quitStatus, plgnQueue, evntQueue):
    self.key = plugin.__pluginable__.key
    self.setIssuerData('plugin', self.key)
    self.tpsMon = TpsMonitor(Settings.Kernel.MaxExecutorTicksPerSec)
    self.quitting = False
    self.initialized = False
    self.programInitDone = False
    self.plugin = plugin
    self.quitStatus = quitStatus
    self.plgnQueue = plgnQueue
    self.evntQueue = evntQueue
    self.plugin.executor = self
    self.inputNodes = Namespace()
    self.evntHandlers = Namespace(
      Config = [self.configure],
      Init = [self.initPlugin],
      Quit = [self.quit],
      GlobalSettings = [self.setGlobalSettings],
      ProgramInitDone = [self.setProgramInit]
    )
    self.criticalExceptions = ['Init', 'Config']

  def updateLoop(self):
    while not self.quitting:
      if mh.get(self.quitStatus): break
      while not mh.empty(self.plgnQueue):
        event = mh.pop(self.plgnQueue)
        self.handleEvent(event)
      if self.initialized:
        if self.programInitDone or not Settings.Kernel.PluginAwaitProgramInit:
          self.tickPlugin()
      self.tpsMon.tick()

  def handleEvent(self, event):
    try: handlers = self.evntHandlers[event.id]
    except KeyError:
      Warn(self, f'Unhandled event "{event.id}"')
      return
    for handler in handlers:
      try: handler(event)
      except (PluginStartupError, PluginRuntimeError) as exc:
        ExecutorExcEvent(self, True, exc)
        self.quitting = True
      except Exception as exc:
        ExecutorExcEvent(self, False, PluginEventError(self.plugin, event.id, exc))

  def tickPlugin(self):
    if Settings.Logger.enablePluginTps:
      if self.tpsMon.newTpsReading: Debug(self, f'TPS = {self.tpsMon.tps}')
    try: self.plugin.update()
    except Exception as exc:
      ExecutorExcEvent(self, True, PluginTickError(self.plugin, exc))

  def quitProgram(self):
    ExecutorEvent(self, 'StopProgram')
    self.quit()

  # Internal event handlers

  def initPlugin(self, event):
    Info(self, f'Plugin init starts')
    try:
      self.plugin.init()
      self.initialized = True
    except Exception as exc:
      raise PluginInitError(self.plugin, exc)
    bareNodes = {key:{k:v for k,v in node.items() if k != 'handler'} for
      key, node in self.inputNodes.items()}
    ExecutorEvent(self, 'InitDoneState', pluginKey=self.key, state=True,
      nodes=bareNodes)
    Info(self, f'Plugin init done')

  def configure(self, event):
    for path, value in event.data.items():
      try: eval(f'self.plugin.cnf.{path}')
      except AttributeError as exc: raise PluginConfigError(self.plugin, path, exc)
      if type(value) == str: value = f'"{value}"'
      exec(f'self.plugin.cnf.{path} = {value}')

  def setGlobalSettings(self, event):
    data = event.data
    for key, val in data.items():
      if type(val) == str: val = f'"{val}"'
      elif type(val) == datetime:
        val = f"datetime.strptime('{val}', '%Y-%m-%d %H:%M:%S.%f')"
      exec(f'Settings.{key} = {val}')
    self.tpsMon.setTarget(Settings.Kernel.MaxExecutorTicksPerSec)

  def setProgramInit(self, event):
    self.programInitDone = True
    try:
      pluginHandler = self.plugin.onProgramInit
      Info(self, 'Executing on-program-init method')
    except AttributeError: return
    pluginHandler(event)

  def quit(self, event=None):
    self.quitting = True
    self.plugin.quit()


def runPlugin(plugin, quitStatus, plgnQueue, evntQueue):
  executor = Executor(plugin, quitStatus, plgnQueue, evntQueue)
  try: executor.updateLoop()
  except KeyboardInterrupt:
    executor.quitProgram()
