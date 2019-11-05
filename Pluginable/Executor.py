import multiprocessing as mpr
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace
from Pluginable.Command import Command

class Executor(Logger):
  def __init__(self, plugin, forceQuit, plgnQueue, cmndQueue, evntQueue, logLock):
    super().__init__((f'{plugin.scope}.{plugin.key}', 'Executor'), 'plugin', logLock)
    self.quitting = False
    self.plugin = plugin
    self.forceQuit = forceQuit
    self.plgnQueue = plgnQueue
    self.cmndQueue = cmndQueue
    self.evntQueue = evntQueue
    self.plugin.executor = self
    self.cmndHandlers = Namespace(
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
      forceQuit = self.forceQuit.value
      if forceQuit: break
      incoming = []
      while not self.plgnQueue.empty():
        try: command = self.plgnQueue.get()
        except BrokenPipeError: break
        try: self.cmndHandlers[command.what](**command.getArgs())
        except:
          self.quitting = True
          raise

  def sendQuit(self):
    self.cmndQueue.put(Command('quit'))

  # Command handlers

  def configure(self, data):
    for path, value in data.items():
      try: eval(f'self.plugin.cnf.{path}')
      except AttributeError:
        self.logWarn(f'Config error in {self.plugin.key}: path {path} does not exist')
      if type(value) == str: value = f'"{value}"'
      exec(f'self.plugin.cnf.{path} = {value}')

  def tickPlugin(self):
    try: self.plugin.update()
    except Exception as exc:
      self.logError(f'Error during tick in plugin {self.plugin.key}')
      self.cmndQueue.put(Command('error', exception=exc,
        key=self.plugin.key, type='tick'))
      raise

  def handleEvent(self, event):
    self.evntHandlers[event.key](event)

  def quit(self):
    self.quitting = True
    self.plugin.quit()

  # Methods called by the Plugin

  def addEvtHandler(self, key, method):
    self.evntHandlers[key] = method
    self.cmndQueue.put(Command('addEvtHandler', key=key, plugin=self.plugin.key))

  def pushEvnt(self, event):
    self.evntQueue.put(event)

  def pushTask(self, task):
    self.taskQueue.put(task)


def runPlugin(plugin, forceQuit, plgnQueue, cmndQueue, evntQueue, logLock):
  executor = Executor(plugin, forceQuit, plgnQueue, cmndQueue, evntQueue, logLock)
  try: executor.updateLoop()
  except EOFError: pass
  except KeyboardInterrupt:
    executor.sendQuit()
