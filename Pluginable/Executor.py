from datetime import datetime
import multiprocessing as mpr
from traceback import format_tb
from Pluginable.Settings import Settings
from Pluginable.Logger import *
from Pluginable.Namespace import Namespace
from Pluginable.Event import ExecutorEvent
from Pluginable.TpsMonitor import TpsMonitor
import Pluginable.MultiHandler as mh

class Executor(LogIssuer):
  def __init__(self, plugin, quitStatus, plgnQueue, evntQueue):
    self.setIssuerData('plugin', plugin.key)
    self.tpsMon = TpsMonitor(Settings.Kernel.MaxExecutorTicksPerSec)
    self.quitting = False
    self.plugin = plugin
    self.quitStatus = quitStatus
    self.plgnQueue = plgnQueue
    self.evntQueue = evntQueue
    self.plugin.executor = self
    self.evntHandlers = Namespace(
      Config = [self.configure],
      Init = [self.initPlugin],
      Tick = [self.tickPlugin],
      Quit = [self.quit],
      GlobalSettings = [self.setGlobalSettings],
    )
    self.errorMsgs = Namespace(
      cnfg = f'Plugin configuration error ({plugin.key})',
      tick = f'Plugin tick error ({plugin.key})',
      quit = f'Plugin cleanup error ({plugin.key})',
    )

  def updateLoop(self):
    while not self.quitting:
      quitStatus = mh.get(self.quitStatus)
      # Warn(self, type(quitStatus), quitStatus)
      if quitStatus == 1: self.purgeTickEvents()
      elif quitStatus == 2: break
      while not mh.empty(self.plgnQueue):
        event = mh.pop(self.plgnQueue)
        if event.id == 'Tick' and quitStatus: continue
        self.handleEvent(event)
        if event.id == 'Tick': break
    # TODO / NOTE: This method can be improved

  def handleEvent(self, event):
    try: handlers = self.evntHandlers[event.id]
    except KeyError:
      Warn(self, f'Unhandled event "{event.id}"')
      return
    for handler in handlers:
      try: handler(event)
      except Exception as exc:
        message = self.errorMsgs[event.id] if event.id in self.errorMsgs.keys()\
          else f'An error occurred while handling event "{event.id}"'
        ExecutorEvent(self, 'PluginError', critical=True, message=message,
          **excToKwargs(exc))
        self.quitting = True

  def quitProgram(self):
    ExecutorEvent(self, 'StopProgram')
    self.quit()

  # Internal event handlers

  def initPlugin(self, event):
    Info(self, f'Starting plugin init')
    try: self.plugin.init()
    except Exception as exc:
      message = 'An error occurred during plugin init'
      ExecutorEvent(self, 'PluginError', critical=True, message=message,
        **excToKwargs(exc))
      self.quitting = True

  def configure(self, event):
    for path, value in event.data.items():
      try: eval(f'self.plugin.cnf.{path}')
      except AttributeError:
        Warn(self, f'Config error in {self.plugin.key}: path {path} does not exist')
      if type(value) == str: value = f'"{value}"'
      exec(f'self.plugin.cnf.{path} = {value}')

  def tickPlugin(self, event):
    self.tpsMon.tick()
    if self.tpsMon.newTpsReading: Debug(self, f'TPS = {self.tpsMon.tps}')
    self.plugin.update()

  def setGlobalSettings(self, event):
    data = event.data
    for key, val in data.items():
      try: eval(f'Settings.{key}')
      except (KeyError, AttributeError):
        Warn(self, f'Setting "{key}" does not exist')
        continue
      if type(val) == str: val = f'"{val}"'
      elif type(val) == datetime:
        val = f"datetime.strptime('{val}', '%Y-%m-%d %H:%M:%S.%f')"
      exec(f'Settings.{key} = {val}')

  def purgeTickEvents(self):
    events = []
    while not mh.empty(self.plgnQueue):
      events += [mh.pop(self.plgnQueue)]
    events = [evt for evt in events if evt.id != 'tick']
    for evt in events:
      mh.push(self.plgnQueue, evt)

  def quit(self, event=None):
    self.quitting = True
    self.plugin.quit()


def runPlugin(plugin, quitStatus, plgnQueue, evntQueue):
  executor = Executor(plugin, quitStatus, plgnQueue, evntQueue)
  try: executor.updateLoop()
  except KeyboardInterrupt:
    executor.quitProgram()

def excToKwargs(exception):
  name = exception.__class__.__name__
  info = exception.args[0]
  traceback = ''.join(format_tb(exception.__traceback__))
  return {'name':name, 'info':info, 'traceback':traceback}
