from datetime import datetime
import multiprocessing as mpr
from traceback import format_tb
from Pluginable.Settings import Settings
from Pluginable.Logger import *
from Pluginable.Namespace import Namespace
from Pluginable.Event import ExecutorEvent
import Pluginable.MultiHandler as mh

class Executor(LogIssuer):
  def __init__(self, plugin, forceQuit, plgnQueue, evntQueue):
    self.setIssuerData('plugin', plugin.key)
    self.quitting = False
    self.plugin = plugin
    self.forceQuit = forceQuit
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
      forceQuit = mh.get(self.forceQuit)
      if forceQuit: break
      incoming = []
      while not mh.empty(self.plgnQueue):
        event = mh.pop(self.plgnQueue)
        try: handlers = self.evntHandlers[event.id]
        except KeyError:
          Warn(self, f'Unhandled event "{event.id}"')
          continue
        for handler in handlers:
          try: handler(event)
          except Exception as exc:
            message = self.errorMsgs[event.id] if event.id in self.errorMsgs.keys()\
              else f'An error occurred during handling event "{event.id}"'
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
    self.plugin.update()

  def handleEvent(self, event):
    self.evntHandlers[event.id](event)

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

  def quit(self, event=None):
    self.quitting = True
    self.plugin.quit()


def runPlugin(plugin, forceQuit, plgnQueue, evntQueue):
  executor = Executor(plugin, forceQuit, plgnQueue, evntQueue)
  try: executor.updateLoop()
  except KeyboardInterrupt:
    executor.quitProgram()

def excToKwargs(exception):
  name = exception.__class__.__name__
  info = exception.args[0]
  traceback = ''.join(format_tb(exception.__traceback__))
  return {'name':name, 'info':info, 'traceback':traceback}
