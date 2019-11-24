from Pluginable.Namespace import Namespace
from Pluginable.Logger import Logger
from Pluginable.Event import Event
from Pluginable.Compiler import Compiler
from Pluginable.FileManager import CleanPyCache
import multiprocessing as mpr
from time import sleep

class Program(Logger):
  def __init__(self):
    self.manager = mpr.Manager()
    self.logLock = self.manager.Lock()
    super().__init__('Program', 'pluginable', self.logLock)
    self.quitting = False
    self.tick = 0
    self.evntQueue = self.manager.Queue()
    self.plugins = Namespace()
    self.evntHandlers = {
      'AddHandler': [self.addEvtHandler],
      'PluginError': [self.onError],
      'StopProgram': [self.quit],
    }
    self.noEvtHandlerWarns = []
    self.compiler = Compiler(self)
    self.phase = 'instance'

  def configPlugin(self, pluginKey, kwargs):
    for key, value in kwargs.items():
      exec(f'self.plugins.{pluginKey}.cnf.{key} = {value}')

  def preload(self):
    self.logNote('Starting program init')
    self.compiler.compile()
    self.compiler.load()
    sleep(0.25)
    self.logNote('Program init complete')
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
      plugin.queue.put(Event(None, 'tick'))
    while True:
      try:
        if self.evntQueue.empty(): break
      except EOFError: exit()
      event = self.evntQueue.get()
      try: hndPlugins = self.evntHandlers[event.id]
      except KeyError:
        if event.id not in self.noEvtHandlerWarns:
          self.logWarn(f'Event "{event.id}" has no handlers assigned')
          self.noEvtHandlerWarns.append(event.id)
        continue
      for handler in hndPlugins:
        if callable(handler): handler(event) # Execute internal handler
        else: # Send event to all plugin executors with handlers
          self.plugins[handler].queue.put(Event('evnt', event=event))

  def quit(self, event=None):
    # set program flags
    if self.phase == 'quitting': return
    self.phase = 'quitting'
    self.logNote('Starting cleanup')
    self.quitting = True
    # quit plugins
    for key, plugin in self.plugins.items():
      if self.phase == 'exception': plugin.forceQuit.value = True
      else: plugin.queue.put(Event(None, 'quit'))
    sleep(0.3)
    for key, plugin in self.plugins.items():
      plugin.proc.join()
    # working directory cleanup
    self.logInfo('Deleting temporary files')
    CleanPyCache()
    self.compiler.removeTemp()

  # Methods called by plugins' executors

  def addEvtHandler(self, event):
    try: self.evntHandlers[event.eventKey] += [event.plugin]
    except KeyError: self.evntHandlers[event.eventKey] = [event.plugin]

  def onError(self, event):
    prefix = ['PluginReset', 'Critical'][event.critical]
    self.logError(f'{prefix}: {event.message}\n' + event.traceback + \
      f'{event.name}: {event.info}')
    self.phase = 'exception'
    if event.critical: self.quit()
