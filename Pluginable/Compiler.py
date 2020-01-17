import multiprocessing as mpr
from time import sleep
import os
from Pluginable.Executor import runPlugin
from Pluginable.Logger import *
from Pluginable.Settings import Settings
from Pluginable.Namespace import Namespace
from Pluginable.FileManager import ifnmkdir, rmtree
from Pluginable.Event import KernelEvent
from Pluginable.Exceptions import *
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
        raise CompilerNoDirectoryError(path) from None
      total = len(keys)
      for index, pluginKey in enumerate(keys):
        if pluginKey in self.pluginsToOmit: continue
        Info(self, f'Compiling ({index+1} of {total}) "{path}/{pluginKey}"')
        self.compilePlugin(path, pluginKey)

  def compilePlugin(self, directory, pluginKey):
    baseDir = f'{directory}/{pluginKey}'
    try: next(os.walk(baseDir))
    except:
      raise CompilerNoDirectoryError(baseDir) from None
    scopeFile = f'{baseDir}/Scope.py'
    configFile = f'{baseDir}/Config.py'
    pluginFile = f'{baseDir}/{pluginKey}.py'
    helperFiles = [f'{baseDir}/{location}' for location in next(os.walk(baseDir))[2]
        if location[:-3] not in ['Scope', 'Config', pluginKey]
        and location[0] != location[0].lower()
        and location.endswith('.py')]

    target = f'./{self.target}/{pluginKey}.py'
    ifnmkdir(self.target)
    open(target, 'w+').close()

    allCode = Settings.Compiler.data.compilationPrefix
    sourceFileLines = [['_prefix_', allCode.count('\n')]]
    filesOrdered = [
      ('Scope.py', scopeFile), ('Config.py', configFile),
      *[(x.split('/')[-1], x) for x in helperFiles],
      (f'{pluginKey}.py', pluginFile),
    ]
    for name, chunk in filesOrdered:
      try:
        code = open(chunk).read()
        allCode += code
        sourceFileLines += [[name, code.count('\n')]]
      except FileNotFoundError:
        raise CompilerMissingFileError(chunk) from None
    with open(target, 'a', newline='\n') as f:
      f.write(allCode)
    pluginData = Namespace(
      key=pluginKey,
      directory = directory,
      loaded = False,
      sourceFileLines = sourceFileLines,
    )
    try: exec(allCode)
    except SyntaxError as exc:
      raise PluginSyntaxError(pluginData, exc) from None
    except Exception as exc:
      raise PluginLoadError(pluginData, exc) from None
    self.prog.plugins[pluginKey] = pluginData

  def load(self):
    Note(self, 'Loading plugins')
    plugins = []
    try: files = [f for f in next(os.walk(self.target))[2] if f.endswith('.py')]
    except StopIteration:
      raise CompilerNoDirsAddedError() from None
    total = len(files)
    for index, filename in enumerate(files):
      pluginKey = filename[:-3]
      Info(self, f'Loading ({index+1} of {total}) "{pluginKey}"')
      self.loadPlugin(pluginKey)

  def loadPlugin(self, pluginKey):
    try: exec(f'from {self.target} import {pluginKey} as plugin')
    except Exception as exc:
      raise PluginLoadError(self.prog.plugins[pluginKey], exc)

    try: PluginClass = eval(f'plugin.{pluginKey}')
    except AttributeError:
      raise CompilerMissingClassError(pluginKey, pluginKey) from None
    instance = PluginClass(pluginKey)
    for key, value in self.prog.plugins[pluginKey].items():
      instance.__pluginable__[key] = value

    try: instance.cnf = eval('plugin.Config')
    except AttributeError:
      raise CompilerMissingClassError(pluginKey, 'Config') from None

    queue = self.prog.manager.Queue()
    mh.push(queue, KernelEvent('GlobalSettings', data=self.prog.settings))
    try:
      config = self.prog.pluginConfigs[pluginKey]
      mh.push(queue, KernelEvent('Config', data=config))
    except KeyError: pass # No changes in plugin config
    mh.push(queue, KernelEvent('Init'))
    quitStatus = self.prog.manager.Value('i', 0)
    proc = mpr.Process(target=runPlugin, args=[instance, quitStatus, queue,
      self.prog.evntQueue])
    proc.start()
    self.prog.plugins[pluginKey].proc = proc
    self.prog.plugins[pluginKey].queue = queue
    self.prog.plugins[pluginKey].quitStatus = quitStatus
    self.prog.plugins[pluginKey].initDone = False
    self.prog.plugins[pluginKey].inputNodes = {}
    self.prog.plugins[pluginKey].loaded = True

  def removeTemp(self):
    try: rmtree(self.target)
    except FileNotFoundError: pass
