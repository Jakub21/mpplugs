import multiprocessing as mpr
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace
from Pluginable.Event import Event

class Executor(Logger):
  def __init__(self, plugin, forceQuit, plgnQueue, evntQueue, logLock):
    super().__init__((f'{plugin.scope}.{plugin.key}', 'Executor'), 'plugin', logLock)
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
    self.evntHandlers = Namespace()
    self.logInfo(f'Initializing plugin {plugin.key}')
    self.plugin.init()

  def updateLoop(self):
    while not self.quitting:
      try: forceQuit = self.forceQuit.value
      except FileNotFoundError: return
      if forceQuit: break
      incoming = []
      while not self.plgnQueue.empty():
        event = self.plgnQueue.get()
        try: handler = self.evntHandlers[event.key]
        except KeyError:
          self.logWarn(f'Error: No internal handler')
        try: handler(event)
        except:
          self.logError(f'An error occurred during handling event "{event.key}"')
          self.quitting = True
          raise

  def quitProgram(self):
    self.evntQueue.put(Event('quit'))

  # Internal event handlers

  def configure(self, event):
    for path, value in event.items():
      try: eval(f'self.plugin.cnf.{path}')
      except AttributeError:
        self.logWarn(f'Config error in {self.plugin.key}: path {path} does not exist')
      if type(value) == str: value = f'"{value}"'
      exec(f'self.plugin.cnf.{path} = {value}')

  def tickPlugin(self, event):
    try: self.plugin.update()
    except Exception as exc:
      self.logError(f'Error during tick in plugin {self.plugin.key}')
      self.cmndQueue.put(Event('error', exception=exc,
        source=self.plugin.key, type='tick'))
      raise

  def handleEvent(self, event):
    self.evntHandlers[event.key](event)

  def quit(self, event=None):
    self.quitting = True
    self.plugin.quit()

  # Methods called by the Plugin

  def addEvtHandler(self, key, method):
    self.evntHandlers[key] = method
    self.evntQueue.put(Event('addEvtHandler', evtkey=key, plugin=self.plugin.key))

  def pushEvnt(self, event):
    self.evntQueue.put(event)

  def pushTask(self, task):
    self.taskQueue.put(task)


def runPlugin(plugin, forceQuit, plgnQueue, evntQueue, logLock):
  executor = Executor(plugin, forceQuit, plgnQueue, evntQueue, logLock)
  try: executor.updateLoop()
  except (EOFError, BrokenPipeError): pass
  except KeyboardInterrupt:
    executor.quitProgram()
