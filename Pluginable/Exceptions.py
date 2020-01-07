
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

class CompilerSyntaxError(CompilerError):
  def __init__(self, pluginKey, className):
    super().__init__(f'Failed to find class "{className}" in plugin {pluginKey}')

# Plugin / Executor

class PluginConfigError(Exception):
  def __init__(self, pluginKey, configPath):
    super().__init__(f'Plugin {pluginKey}: config "{configPath}" does not exist')
