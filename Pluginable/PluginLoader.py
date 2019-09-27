from os import walk
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace
from Pluginable.FileManager import ifnmkdir, rmtree

class PluginLoader(Logger):
  def __init__(self, prog):
    super().__init__(('Pluginable', self.__class__.__name__), 'pluginable')
    self.prog = prog
    self.directories = []
    self.target = self.prog.settings.tempPluginsDirectory

  def addDirectory(self, directory):
    self.directories.append(directory)

  def load(self):
    plugins = []
    for directory in self.directories:
      path = f'./Plugins/{directory}/'
      keys = [d for d in next(walk(path))[1] if not d.startswith('__')]
      for pluginKey in keys:
        plugin = self.loadPlugin(path, pluginKey)
        plugins += [plugin]
        self.prog.plugins[plugin.key] = plugin

  def init(self):
    plugins = list(self.prog.plugins.values())
    for plugin in self.orderByDependencies(plugins):
      try: plugin.init()
      except KeyboardInterrupt:
        raise
      except:
        self.logError(f'An error occurred during init of plugin "{plugin.key}"')
        raise

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
    rmtree(self.target)

    PluginClass = eval(f'plugin.{pluginKey}')
    PluginClass.scope = scopeName
    PluginClass.key = pluginKey
    instance = PluginClass(self.prog)

    PluginClass.tasks = Namespace()
    for k in dir(eval('plugin')):
      if k[0] == '_' and k[1].lower() != k[1]:
        task = eval(f'plugin.{k}')
        task.key = k[1:]
        task.plugin = instance
        PluginClass.tasks[k[1:]] = task
    PluginClass.cnf = eval('plugin.Config')

    return instance

  @staticmethod
  def orderByDependencies(plugins):
    for iter in range(len(plugins)):
      for index, plugin in enumerate(plugins):
        name = plugin.key
        dependencies = [i for i, p in enumerate(plugins) if p.key in plugin.DEPENDENCIES]
        try: target = max(dependencies) + 1
        except ValueError: # no dependencies
          continue
        plugins.remove(plugin)
        plugins.insert(target, plugin)
        break
    return plugins
