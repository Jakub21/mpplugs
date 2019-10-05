import traceback
import asyncio
from Pluginable.Queue import Queue
from Pluginable.PluginLoader import PluginLoader
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace
from Pluginable.FileManager import CleanPyCache

class Program(Logger):
  def __init__(self):
    super().__init__(('Pluginable', self.__class__.__name__), 'pluginable')
    self.tick = 0
    self.taskQueue = Queue()
    self.loaded = False
    self.initialized = False
    self.running = False
    self.properQuit = False
    self.settings = Namespace(
      tasksPerTick = 1,
      raiseOnTaskError = False,
      logTasksExecution = True,
      tempPluginsDirectory = '_pluginable',
      slowTempDeletion = False,
    )
    self.plgLoader = PluginLoader(self)
    self.plugins = Namespace() # filled by loader

  def config(self, key, val):
    '''Change pluginable defined settings'''
    if key not in self.settings.keys():
      raise KeyError('No such setting found')
    self.settings[key] = val

  def addConfig(self, key, val):
    '''Add custom settings
    (in same namespace as pluginable config so beware of overlapping)'''
    self.settings[key] = val

  def pluginConfig(self, pluginKey, property, value):
    if not self.loaded:
      raise ValueError('Plugins must be loaded before they can be configured')
    if self.initialized:
      raise ValueError('Plugins can not be configured after they are initialized')
    try: config = self.plugins[pluginKey].cnf
    except KeyError:
      self.logError('Tried to configure plugin that does not exist')
      raise
    cmd = 'config'
    for key in property.split('.'):
      cmd += f'.{key}'
    if type(value) == str: value = f'"{value}"'
    try: eval(cmd)
    except:
      path = '.'.join([pluginKey]+cmd.split('.')[1:])
      self.logWarn(f'Could not configure plugin, key "{path}" does not exist')
      return
    cmd += f' = {value}'
    exec(cmd)

  def loadPlugins(self):
    self.logInfo('Loading plugins')
    self.plgLoader.load()
    self.logInfo('Deleting __pycache__ directories')
    CleanPyCache()
    self.loaded = True

  def initPlugins(self):
    self.logInfo('Initializing plugins')
    self.plgLoader.init()
    self.initialized = True

  async def run(self):
    if not self.initialized:
      self.logError('Please exec program.initPlugins first')
      return
    self.logInfo('Starting program')
    self.running = True
    try:
      while self.running:
        await self.update()
    except KeyboardInterrupt:
      self.logWarn('Keyboard Interrupt')
    self.quit()

  async def update(self):
    for x in range(self.settings.tasksPerTick):
      if not self.execLastTask(): break
    try:
      await asyncio.gather( \
        *[plugin.update() for plugin in self.plugins.values()])
    except KeyboardInterrupt: raise
    except Exception as err:
      self.logError(f'An error occurred during tick of a plugin')
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
    self.running = False
    self.properQuit = True
    plugins = [p for k, p in self.plugins.items()]
    for plugin in self.plgLoader.orderByDependencies(plugins)[::-1]:
      plugin.quit()

  def pushTask(self, task):
    self.taskQueue.push(task)
