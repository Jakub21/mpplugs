from Pluginable.Namespace import Namespace

# Compiler

class CompilerError(Exception): pass

class CompilerNoDirectoryError(CompilerError):
  def __init__(self, path):
    super().__init__(f'Plugins directory added to config does not exist ({path})')

class CompilerNoDirsAddedError(CompilerError):
  def __init__(self):
    super().__init__(f'No plugin directories were added to compiler config')

class CompilerMissingFileError(CompilerError):
  def __init__(self, path):
    super().__init__(f'Missing required plugin file ({path})')

class CompilerMissingClassError(CompilerError):
  def __init__(self, pluginKey, className):
    super().__init__(f'Failed to find class "{className}" in plugin {pluginKey}')

class CompilerSyntaxError(CompilerError):
  def __init__(self, pluginKey, original):
    info = original.args[1]
    info = Namespace(file=info[0], lineno=info[1], offset=info[2], code=info[3])
    super().__init__(f'There is a syntax error in plugin {pluginKey}\n' +\
      f'  File "{info.file}", line {info.lineno}\n    {info.code}   '+\
      ' '*info.offset+f'^\nSyntaxError: invalid syntax')
    self.noTraceback = True

# Plugin / Executor

class PluginConfigError(Exception):
  def __init__(self, pluginKey, configPath):
    super().__init__(f'Plugin {pluginKey}: config "{configPath}" does not exist')
#
#   File "D:\GoogleDrive\Coding\Repositories\Python\Rover-Related\RoverSoft\__PluginableCache_Controller\Interface.py", line 54
#     self.statusWidgets = {}a
#                            ^
# SyntaxError: invalid syntax
