from os import walk
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace

class PluginLoader(Logger):
  def __init__(self, prog):
    super().__init__(('Pluginable', self.__class__.__name__), 'pluginable')
    self.prog = prog
    self.directories = []

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
    for plugin in self.orderByDependencies(plugins):
      try: plugin.init()
      except KeyboardInterrupt:
        raise
      except:
        self.logError(f'An error occurred during init of plugin "{plugin.key}"')
        raise

  def loadPlugin(self, directory, pluginKey):
    scope = directory.replace('\\','/').split('/')[-2]
    # Read code files
    baseDir = f'{directory}{pluginKey}/'
    scopeFile = open(f'{baseDir}Scope.py').read()
    configFile = open(f'{baseDir}Config.py').read()
    pluginFile = open(f'{baseDir}{pluginKey}.py').read()
    helperFiles = [open(f'{baseDir}{location}').read()
      for location in next(walk(f'{baseDir}'))[2] if location != pluginKey+'.py' and\
        location[0] != location[0].lower() and location.endswith('.py')]
    taskFiles = [open(f'{baseDir}{location}').read()
      for location in next(walk(f'{baseDir}'))[2]
      if location[1] != location[1].lower() and location.endswith('.py')
      and location[0] == '_']

    # Preparations
    preScopeLocals = list(set(locals().keys()))
    try: exec(scopeFile)
    except SyntaxError:
      self.logError(f'Syntax Error in {scope}::{pluginKey} (Scope)')
      raise
    for file in helperFiles:
      try: exec(file)
      except SyntaxError:
        self.logError(f'Syntax Error in {scope}::{pluginKey} (Helper)')
        raise
    globals().update({k:v for k, v in locals().items() if k not in preScopeLocals})

    preExecLocals = list(set(locals().keys()))

    # Execute code
    try: exec(configFile)
    except SyntaxError:
      self.logError(f'Syntax Error in {scope}::{pluginKey} (Config)')
      raise
    try: exec(pluginFile)
    except SyntaxError:
      self.logError(f'Syntax Error in {scope}::{pluginKey} (Plugin Core)')
      raise
    for file in taskFiles:
      try: exec(file)
      except SyntaxError:
        self.logError(f'Syntax Error in {scope}::{pluginKey} (Task)')
        raise
    del file

    # Wrap a plugin
    elements = [k for k in locals().keys() if k not in ['preExecLocals']+preExecLocals]
    PluginCls = eval(pluginKey)
    config = eval('Config')
    helpers = [eval(elm) for elm in elements if elm[0] != elm[0].lower() and \
      elm not in [pluginKey, 'Config'] + preExecLocals]
    tasks = []
    for elm in elements:
      if elm.startswith('_') and elm[1] != elm[1].lower():
        tasks += [eval(elm)]
    PluginCls.scope = scope
    PluginCls.key = PluginCls.__name__
    plugin = PluginCls(self.prog)
    plugin.cnf = config
    for Helper in helpers:
      name = Helper.__name__
      name = name[0].lower() + name[1:]
      plugin.__dict__[name] = Helper()
    for task in tasks:
      key = task.__name__[1:]
      key = key[0] + key[1:]
      task.key = key
      task.plugin = plugin
      plugin.tasks[key] = task
    return plugin

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
