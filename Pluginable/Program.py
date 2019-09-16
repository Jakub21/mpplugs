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
    self.settings = Namespace(
      tasksPerTick = 1,
    )
    self.plugins = Namespace() # filled by loader

  def config(self, key, val):
    if key not in self.settings.keys():
      raise KeyError('No such setting found')
    self.settings[key] = val

  def initPlugins(self):
    self.logNote('Loading plugins')
    self.plgLoader.load()
    for key, plugin in self.plugins.items():
      self.logDebug(key, plugin)
      for k, task in plugin.tasks.items():
        self.logDebug('  ', k, task)
      print()
    self.initialized = True

  def run(self):
    if not self.initialized:
      self.logError('Please exec program.initPlugins first')
      return
    self.logNote('Starting program loop')
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
    return True

  def quit(self):
    for key, plugin in self.plugins.items():
      plugin.quit()

  def pushTask(self, task):
    self.taskQueue.push(task)

  def __del__(self):
    CleanPyCache()
