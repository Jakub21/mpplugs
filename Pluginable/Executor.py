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
    self.setIssuerData('plugin', plugin.key)
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
      except Exception as exc:
        critical = event.id in self.criticalExceptions
        ExecutorExcEvent(self, critical, exc)
        self.quitting = critical or self.quitting

  def tickPlugin(self):
    if Settings.Logger.enablePluginTps:
      if self.tpsMon.newTpsReading: Debug(self, f'TPS = {self.tpsMon.tps}')
    try: self.plugin.update()
    except Exception as exc:
      Error(self, f'An error occurred during tick of plugin {self.plugin.key}')
      ExecutorExcEvent(self, True, exc)

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
      Error(self, f'An error occurred during init of plugin {self.plugin.key}')
      raise
    bareNodes = {key:{k:v for k,v in node.items() if k != 'handler'} for
      key, node in self.inputNodes.items()}
    ExecutorEvent(self, 'InitDoneState', pluginKey=self.plugin.key, state=True,
      nodes=bareNodes)
    Info(self, f'Plugin init done')

  def configure(self, event):
    for path, value in event.data.items():
      try: eval(f'self.plugin.cnf.{path}')
      except AttributeError:
        raise PluginConfigError(self.plugin.key, path)
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
