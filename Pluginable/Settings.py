from Pluginable.Namespace import Namespace
from Pluginable.Event import Event

Settings = Namespace(
  Compiler = Namespace(
    cacheDirectory = 'PluginableCache',
    pluginDirectories = [],
    omitPlugins = [],
    data = Namespace(
      compilationPrefix = '''
# File compiled by pluginable, any edits will be automatically overwritten

# from Pluginable.Logger import DEBUG, INFO, NOTE, WARN, ERROR
from Pluginable.Settings import Settings

# Plugin code

'''
    )
  ),

  Logger = Namespace(
    timeFormat = '24h',
  ),

  Text = Namespace(
    ErrorMessages = Namespace(
      dummy = 'Dummy error from {key}',
    )
  )
)
