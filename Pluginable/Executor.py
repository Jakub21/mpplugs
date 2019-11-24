import multiprocessing as mpr
from traceback import format_tb
from Pluginable.Logger import *
from Pluginable.Namespace import Namespace
from Pluginable.Event import ExecutorEvent

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
      cnfg = self.configure,
      tick = self.tickPlugin,
      evnt = self.handleEvent,
      quit = self.quit
    )
    self.errorMsgs = Namespace(
      cnfg = f'Plugin configuration error ({plugin.key})',
      tick = f'Plugin tick error ({plugin.key})',
      quit = f'Plugin cleanup error ({plugin.key})',
    )
    Info(self, f'Starting plugin init')
    self.plugin.init()

  def updateLoop(self):
    while not self.quitting:
      try: forceQuit = self.forceQuit.value
      except FileNotFoundError: return
      if forceQuit: break
      incoming = []
      while not self.plgnQueue.empty():
        event = self.plgnQueue.get()
        try: handler = self.evntHandlers[event.id]
        except KeyError:
          Warn(self, f'Error: No internal handler')
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

  def configure(self, event):
    for path, value in event.items():
      try: eval(f'self.plugin.cnf.{path}')
      except AttributeError:
        Warn(self, f'Config error in {self.plugin.key}: path {path} does not exist')
      if type(value) == str: value = f'"{value}"'
      exec(f'self.plugin.cnf.{path} = {value}')

  def tickPlugin(self, event):
    self.plugin.update()

  def handleEvent(self, event):
    self.evntHandlers[event.key](event)

  def quit(self, event=None):
    self.quitting = True
    self.plugin.quit()


def runPlugin(plugin, forceQuit, plgnQueue, evntQueue):
  executor = Executor(plugin, forceQuit, plgnQueue, evntQueue)
  try: executor.updateLoop()
  except (EOFError, BrokenPipeError): pass
  except KeyboardInterrupt:
    executor.quitProgram()

def excToKwargs(exception):
  name = exception.__class__.__name__
  info = exception.args[0]
  traceback = ''.join(format_tb(exception.__traceback__))
  return {'name':name, 'info':info, 'traceback':traceback}
