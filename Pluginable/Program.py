from Pluginable.Namespace import Namespace
from Pluginable.Logger import *
from Pluginable.Event import StockEvent
from Pluginable.Compiler import Compiler
from Pluginable.FileManager import CleanPyCache
import Pluginable.MultiHandler as mh
import multiprocessing as mpr
from time import sleep

class Program(LogIssuer):
  def __init__(self):
    self.manager = mpr.Manager()
    self.setIssuerData('kernel', 'Program')
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
    Note(self, 'Starting program init')
    self.compiler.compile()
    self.compiler.load()
    sleep(0.25)
    Note(self, 'Program init complete')
    self.phase = 'preloaded'

  def run(self):
    Info(self, 'Starting')
    self.phase = 'running'
    while not self.quitting:
      try: self.update()
      except KeyboardInterrupt: break
      except: self.phase = 'exception'; raise
    self.quit()

  def update(self):
    for plugin in self.plugins.values():
      mh.push(plugin.queue, StockEvent('tick'))
    while not mh.empty(self.evntQueue):
      event = mh.pop(self.evntQueue)
      try: hndPlugins = self.evntHandlers[event.id]
      except KeyError:
        if event.id not in self.noEvtHandlerWarns:
          Warn(self, f'Event "{event.id}" has no handlers assigned')
          self.noEvtHandlerWarns.append(event.id)
        continue
      except AttributeError:
        Warn(self, f'There was a boolean in event queue')
        continue
      for handler in hndPlugins:
        if callable(handler): handler(event) # Execute internal handler
        else: # Send event to all plugin executors with handlers
          mh.push(self.plugins[handler].queue, event)

  def quit(self, event=None):
    # set program flags
    if self.phase == 'quitting': return
    self.phase = 'quitting'
    Note(self, 'Starting cleanup')
    self.quitting = True
    # quit plugins
    for key, plugin in self.plugins.items():
      if self.phase == 'exception': mh.set(plugin.forceQuit, True)
      else: mh.push(plugin.queue, StockEvent('quit'))
    sleep(0.3)
    for key, plugin in self.plugins.items():
      plugin.proc.join()
    # working directory cleanup
    Info(self, 'Deleting temporary files')
    CleanPyCache()
    self.compiler.removeTemp()

  # Methods called by plugins' executors

  def addEvtHandler(self, event):
    try: self.evntHandlers[event.eventKey] += [event.plugin]
    except KeyError: self.evntHandlers[event.eventKey] = [event.plugin]

  def onError(self, event):
    prefix = ['PluginReset', 'Critical'][event.critical]
    Error(self, f'{prefix}: {event.message}\n' + event.traceback + \
      f'{event.name}: {event.info}')
    self.phase = 'exception'
    if event.critical: self.quit()
