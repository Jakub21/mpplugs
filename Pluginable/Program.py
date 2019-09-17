import traceback
from Pluginable.Queue import Queue
from Pluginable.PluginLoader import PluginLoader
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace
from Pluginable.CleanPyCache import CleanPyCache

class Program(Logger):
  def __init__(self):
    super().__init__(__file__, 'pluginable')
    self.tick = 0
    self.taskQueue = Queue()
    self.plgLoader = PluginLoader(self)
    self.initialized = False
    self.running = False
    self.properQuit = False
    self.settings = Namespace(
      tasksPerTick = 1,
      raiseOnTaskError = False,
    )
    self.plugins = Namespace() # filled by loader

  def config(self, key, val):
    if key not in self.settings.keys():
      raise KeyError('No such setting found')
    self.settings[key] = val

  def initPlugins(self):
    self.logInfo('Loading plugins')
    self.plgLoader.load()
    self.initialized = True

  def run(self):
    if not self.initialized:
      self.logError('Please exec program.initPlugins first')
      return
    self.logInfo('Starting program')
    self.running = True
    try:
      while self.running:
        self.update()
    except KeyboardInterrupt:
      self.logWarn('Keyboard Interrupt')
    self.quit()

  def update(self):
    for x in range(self.settings.tasksPerTick):
      if not self.execLastTask(): break
    for key, plugin in self.plugins.items():
      try: plugin.update()
      except KeyboardInterrupt:
        raise
      except:
        self.logError(f'An error occurred during tick of plugin "{key}"')
        raise
    self.tick += 1

  def execLastTask(self):
    try: task = self.taskQueue.pop()
    except IndexError: return False
    try: task.execute()
    except KeyboardInterrupt:
      raise
    except:
      trbk = traceback.format_exc()
      msg = 'An error occurred during execution of task'
      self.logError(f'{msg} "{task.plugin.key}.{task.key}"\n{trbk}')
      if self.settings.raiseOnTaskError:
        raise
    return True

  def quit(self):
    if self.properQuit: return
    self.logNote('Starting quit procedure')
    self.properQuit = True
    for key, plugin in self.plugins.items():
      plugin.quit()
    self.logInfo('Deleting __pycache__ directories')
    CleanPyCache()

  def pushTask(self, task):
    self.taskQueue.push(task)
