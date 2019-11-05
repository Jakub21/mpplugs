import multiprocessing as mpr
from time import sleep
from os import walk
from Pluginable.Executor import runPlugin
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace
from Pluginable.FileManager import ifnmkdir, rmtree

class PluginLoader(Logger):
  def __init__(self, prog):
    super().__init__(('Pluginable', 'PluginLoader'), 'pluginable', prog.logLock)
    self.prog = prog
    self.directories = []
    self.pluginsToOmit = []
    self.target = ''

  def load(self):
    self.directories = self.prog.settings.loaderDirectories
    self.pluginsToOmit = self.prog.settings.loaderOmit
    self.target = self.prog.settings.loaderTemp
    plugins = []
    self.logNote(f'List of directories: {self.directories}')
    for directory in self.directories:
      path = f'./Plugins/{directory}/'
      keys = [d for d in next(walk(path))[1] if not d.startswith('__')]
      for pluginKey in keys:
        self.logNote(f'Loading plugin "{pluginKey}"')
        if pluginKey in self.pluginsToOmit: continue
        plugin = self.loadPlugin(path, pluginKey)
        plugins += [plugin]
        self.prog.plugins[plugin.key] = plugin

  def loadPlugin(self, directory, pluginKey):
    scopeName = directory.replace('\\','/').split('/')[-2]

    baseDir = f'{directory}{pluginKey}/'
    scopeFile = f'{baseDir}Scope.py'
    configFile = f'{baseDir}Config.py'
    pluginFile = f'{baseDir}{pluginKey}.py'
    helperFiles = [f'{baseDir}{location}' for location in next(walk(baseDir))[2]
        if location[:-3] not in ['Scope', 'Config', pluginKey]
        and location[0] != location[0].lower()
        and location.endswith('.py')]
    taskFiles = [f'{baseDir}{location}' for location in next(walk(baseDir))[2]
      if location[1] != location[1].lower()
      and location.endswith('.py')
      and location[0] == '_']

    target = f'./{self.target}/{pluginKey}.py'
    ifnmkdir(self.target)
    open(target, 'w+').close()
    f = open(target, 'a', newline='\n')
    for file in [scopeFile, configFile] + helperFiles + taskFiles + [pluginFile]:
      f.write(open(file).read())
    f.close()

    exec(f'import {self.target}.{pluginKey} as plugin')

    PluginClass = eval(f'plugin.{pluginKey}')
    instance = PluginClass(scopeName, pluginKey, self.prog.logLock)

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
      self.prog.cmndQueue, self.prog.evntQueue, self.prog.logLock])
    proc.start()
    return Namespace(key=pluginKey, proc=proc, queue=queue, forceQuit=forceQuit)

  def removeTemp(self):
    try: rmtree(self.target)
    except FileNotFoundError: pass
