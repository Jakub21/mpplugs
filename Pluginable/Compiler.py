import multiprocessing as mpr
from time import sleep
import os
from Pluginable.Executor import runPlugin
from Pluginable.Logger import *
from Pluginable.Settings import Settings
from Pluginable.Namespace import Namespace
from Pluginable.FileManager import ifnmkdir, rmtree
from Pluginable.Event import StockEvent
import Pluginable.MultiHandler as mh

class Compiler(LogIssuer):
  def __init__(self, prog):
    self.setIssuerData('kernel', 'Compiler')
    self.prog = prog

  def compile(self):
    Note(self, 'Compiling plugins')
    target = Settings.Compiler.cacheDirectory
    self.target = f'_{target}_{self.prog.progName}'
    self.directories = Settings.Compiler.pluginDirectories
    self.pluginsToOmit = Settings.Compiler.omitPlugins
    for path in self.directories:
      try: keys = [d for d in next(os.walk(path))[1] if not d.startswith('__')]
      except StopIteration:
        Error(self, f'Can not compile plugins, directory "{path}" does not exist')
        exit()
      total = len(keys)
      for index, pluginKey in enumerate(keys):
        if pluginKey in self.pluginsToOmit: continue
        Info(self, f'Compiling ({index+1} of {total}) "{path}/{pluginKey}"')
        self.compilePlugin(path, pluginKey)

  def compilePlugin(self, directory, pluginKey):
    baseDir = f'{directory}/{pluginKey}'
    scopeFile = f'{baseDir}/Scope.py'
    configFile = f'{baseDir}/Config.py'
    pluginFile = f'{baseDir}/{pluginKey}.py'
    helperFiles = [f'{baseDir}/{location}' for location in next(os.walk(baseDir))[2]
        if location[:-3] not in ['Scope', 'Config', pluginKey]
        and location[0] != location[0].lower()
        and location.endswith('.py')]
    taskFiles = [f'{baseDir}/{location}' for location in next(os.walk(baseDir))[2]
      if location[1] != location[1].lower()
      and location.endswith('.py')
      and location[0] == '_']

    target = f'./{self.target}/{pluginKey}.py'
    ifnmkdir(self.target)
    open(target, 'w+').close()

    f = open(target, 'a', newline='\n')
    f.write(Settings.Compiler.data.compilationPrefix)
    for chunk in [scopeFile, configFile] + helperFiles + taskFiles + [pluginFile]:
      f.write(open(chunk).read())
    f.close()

  def load(self):
    Note(self, 'Loading plugins')
    plugins = []
    try: files = [f for f in next(os.walk(self.target))[2] if f.endswith('.py')]
    except StopIteration:
      Error(self, 'No plugin directories added (Settings.Compiler.pluginDirectories)')
      exit()
    total = len(files)
    for index, filename in enumerate(files):
      pluginKey = filename[:-3]
      Info(self, f'Loading ({index+1} of {total}) "{pluginKey}"')
      self.loadPlugin(pluginKey)

  def loadPlugin(self, pluginKey):
    exec(f'from {self.target} import {pluginKey} as plugin')

    try: PluginClass = eval(f'plugin.{pluginKey}')
    except AttributeError:
      Error(self, f'[{pluginKey}] Main plugin class not found')
      exit()
    instance = PluginClass(pluginKey)

    instance.tasks = Namespace()
    for k in dir(eval('plugin')):
      if k[0] == '_' and k[1].lower() != k[1]:
        task = eval(f'plugin.{k}')
        task.key = k[1:]
        task.plugin = instance
        instance.tasks[k[1:]] = task
    try: instance.cnf = eval('plugin.Config')
    except AttributeError:
      Error(self, f'[{pluginKey}] Config class not found')
      exit()

    queue = self.prog.manager.Queue()
    mh.push(queue, StockEvent('GlobalSettings', data=self.prog.settings))
    try:
      config = self.prog.pluginConfigs[pluginKey]
      mh.push(queue, StockEvent('Config', data=config))
    except KeyError: pass # No changes in plugin config
    mh.push(queue, StockEvent('Init'))
    quitStatus = self.prog.manager.Value('i', 0)
    proc = mpr.Process(target=runPlugin, args=[instance, quitStatus, queue,
      self.prog.evntQueue])
    proc.start()
    pluginData = Namespace(key=pluginKey, proc=proc, queue=queue, quitStatus=quitStatus)
    self.prog.plugins[pluginKey] = pluginData

  def removeTemp(self):
    try: rmtree(self.target)
    except FileNotFoundError: pass
