import multiprocessing as mpr
from time import sleep
import os
from Pluginable.Executor import runPlugin
from Pluginable.Logger import *
from Pluginable.Settings import Settings
from Pluginable.Namespace import Namespace
from Pluginable.FileManager import ifnmkdir, rmtree

class Compiler(LogIssuer):
  def __init__(self, prog):
    self.setIssuerData('kernel', 'Compiler')
    self.prog = prog
    self.target = Settings.Compiler.cacheDirectory
    self.directories = Settings.Compiler.pluginDirectories
    self.pluginsToOmit = Settings.Compiler.omitPlugins

  def compile(self):
    Note(self, 'Compiling plugins')
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
    files = [f for f in next(os.walk(self.target))[2] if f.endswith('.py')]
    total = len(files)
    for index, filename in enumerate(files):
      pluginKey = filename[:-3]
      Info(self, f'Loading ({index+1} of {total}) "{pluginKey}"')
      self.loadPlugin(pluginKey)

  def loadPlugin(self, pluginKey):
    exec(f'from {self.target} import {pluginKey} as plugin')

    PluginClass = eval(f'plugin.{pluginKey}')
    instance = PluginClass(pluginKey)

    instance.tasks = Namespace()
    for k in dir(eval('plugin')):
      if k[0] == '_' and k[1].lower() != k[1]:
        task = eval(f'plugin.{k}')
        task.key = k[1:]
        task.plugin = instance
        instance.tasks[k[1:]] = task
    instance.cnf = eval('plugin.Config')

    queue = self.prog.manager.Queue()
    forceQuit = self.prog.manager.Value('i', 0)
    proc = mpr.Process(target=runPlugin, args=[instance, forceQuit, queue,
      self.prog.evntQueue])
    proc.start()
    pluginData = Namespace(key=pluginKey, proc=proc, queue=queue, forceQuit=forceQuit)
    self.prog.plugins[pluginKey] = pluginData

  def removeTemp(self):
    try: rmtree(self.target)
    except FileNotFoundError: pass
