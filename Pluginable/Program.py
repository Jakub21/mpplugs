from Pluginable.Namespace import Namespace
from Pluginable.Logger import Logger
from Pluginable.Event import Event
from Pluginable.PluginLoader import PluginLoader
from Pluginable.FileManager import CleanPyCache
import multiprocessing as mpr
from time import sleep

class Program(Logger):
  def __init__(self):
    self.manager = mpr.Manager()
    self.logLock = self.manager.Lock()
    super().__init__(('Pluginable', 'Program'), 'pluginable', self.logLock)
    self.quitting = False
    self.tick = 0
    self.cmndQueue = self.manager.Queue()
    self.evntQueue = self.manager.Queue()
    self.taskQueue = self.manager.Queue()
    self.plugins = Namespace()
    self.settings = Namespace(
      tasksPerTick = 3,
      loaderTemp = 'tempPlugins',
      loaderDirectories = [],
      loaderOmit = [],
    )
    self.evntHandlers = {
      'addEvtHandler': [self.addEvtHandler],
      'error': [self.onError],
      'quit': [self.quit],
    }
    self.noEvtHandlerWarns = []
    self.plgLoader = PluginLoader(self)
    self.phase = 'instance'

  def config(self, **kwargs):
    for key, val in kwargs.items():
      if key not in self.settings.keys():
        self.logWarn(f'Settings key "{key}" was not found')
        continue
      self.settings[key] = val

  def configPlugin(self, pluginKey, kwargs):
    for key, value in kwargs.items():
      exec(f'self.plugins.{pluginKey}.cnf.{key} = {value}')

  def preload(self):
    self.logInfo('Preloading plugins')
    try: self.plgLoader.load()
    except StopIteration:
      self.logError('Can not load plugins, directory does not exist')
      exit()
    finally:
      pass
      self.logInfo('Deleting __pycache__ directories')
      CleanPyCache()
    sleep(0.25)
    self.phase = 'preloaded'

  def run(self):
    self.logInfo('Starting')
    self.phase = 'running'
    while not self.quitting:
      try: self.update()
      except KeyboardInterrupt: break
      except: self.phase = 'exception'; raise
    self.quit()

  def update(self):
    for plugin in self.plugins.values():
      try: queue = plugin.queue
      except AttributeError: continue
      plugin.queue.put(Event('tick'))
    while not self.evntQueue.empty():
      event = self.evntQueue.get()
      try: hndPlugins = self.evntHandlers[event.key]
      except KeyError:
        if event.key not in self.noEvtHandlerWarns:
          self.logWarn(f'Event "{event.key}" has no handlers assigned')
          self.noEvtHandlerWarns.append(event.key)
        continue
      for handler in hndPlugins:
        if callable(handler): handler(event) # Execute internal handler
        else: # Send event to all plugin executors with handlers
          self.plugins[handler].queue.put(Event('evnt', event=event))
    taskIndex = 0
    while not self.taskQueue.empty() and taskIndex < self.settings.tasksPerTick:
      task = self.taskQueue.get()
      pluginCmd = task.execute()
      self.plugins[task.pluginKey].queue.put(pluginCmd)
      taskIndex += 1

  def quit(self, event=None):
    if self.phase == 'quitting': return
    self.phase = 'quitting'
    self.logNote('Starting standard quit procedure')
    for plugin in self.plugins.values():
      if self.phase == 'exception': plugin.forceQuit = True
      else: plugin.queue.put(Event('quit'))
    sleep(0.3)
    for key, plugin in self.plugins.items(): plugin.proc.join()
    self.quitting = True
    self.logNote('Done')
    self.plgLoader.removeTemp()

  # Methods called by plugins' executors

  def addEvtHandler(self, event):
    try: self.evntHandlers[event.evtkey] += [event.plugin]
    except KeyError: self.evntHandlers[event.evtkey] = [event.plugin]

  def onError(self, event):
    self.phase = 'exception'
    self.exception = event
    exit()
