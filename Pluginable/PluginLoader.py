from os import walk
from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace

class PluginLoader(Logger):
  def __init__(self, prog):
    super().__init__(__file__, 'pluginable')
    self.prog = prog
    self.directories = []

  def addDirectory(self, directory):
    self.directories.append(directory)

  def load(self):
    for directory in self.directories:
      path = f'./Plugins/{directory}/'
      keys = [d for d in next(walk(path))[1] if not d.startswith('__')]
      for pluginKey in keys:
        self.loadPlugin(path, pluginKey)
    for plugin in self.prog.plugins.values():
      plugin.init()

  def loadPlugin(self, directory, pluginKey):
    # Read code files
    baseDir = f'{directory}{pluginKey}/'
    scopeFile = open(f'{baseDir}Scope.py').read()
    configFile = open(f'{baseDir}Config.py').read()
    pluginFile = open(f'{baseDir}{pluginKey}.py').read()
    helperFiles = [open(f'{baseDir}{location}').read()
      for location in next(walk(f'{baseDir}'))[2]
      if location[0] != location[0].lower() and location.endswith('.py')]
    taskFiles = [open(f'{baseDir}{location}').read()
      for location in next(walk(f'{baseDir}'))[2]
      if location[1] != location[1].lower() and location.endswith('.py')
      and location[0] == '_']

    # Preparations
    preScopeLocals = list(set(locals().keys()))
    exec(scopeFile)
    for file in helperFiles: exec(file)
    globals().update({k:v for k, v in locals().items() if k not in preScopeLocals})

    preExecLocals = list(set(locals().keys()))

    # Execute code
    exec(configFile)
    exec(pluginFile)
    for file in taskFiles: exec(file)
    del file

    # Wrap a plugin
    elements = [k for k in locals().keys() if k not in ['preExecLocals']+preExecLocals]
    PluginCls = eval(pluginKey)
    config = eval('Config')
    helpers = [eval(elm) for elm in elements if elm[0] != elm[0].lower() and \
      elm not in [pluginKey, 'Config'] + preExecLocals]
    # tasks = [eval(elm) for elm in elements if elm.startswith('_') and \
    #   elm[1] != elm[1].lower()]
    tasks = []
    for elm in elements:
      if elm.startswith('_') and elm[1] != elm[1].lower():
        tasks += [eval(elm)]

    plugin = PluginCls(self.prog)
    plugin.key = PluginCls.__name__
    plugin.cnf = config
    for Helper in helpers:
      name = Helper.__name__
      name = name[0].lower() + name[1:]
      plugin.__dict__[name] = Helper()
    for task in tasks:
      key = task.__name__[1:]
      key = key[0].lower() + key[1:]
      task.key = key
      task.plugin = plugin
      plugin.tasks[key] = task

    self.prog.plugins[pluginKey] = plugin
