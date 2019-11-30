from Pluginable.Namespace import Namespace
from Pluginable.Event import Event
from Pluginable.LogOutputs import stdout, stderr

Settings = Namespace(
  Compiler = Namespace(
    cacheDirectory = 'PluginableCache',
    pluginDirectories = [],
    omitPlugins = [],
    data = Namespace(
      compilationPrefix = '''
# File compiled by pluginable, any edits will be automatically overwritten
from Pluginable import Plugin, Event
from Pluginable import Settings
from Pluginable.Logger import Debug, Info, Note, Warn, Error

# Plugin code

'''
    )
  ),

  Logger = Namespace(
    timeFormat = '24h',
    timeRelative = False,
    logOutputs = [stdout, ],
    colors = Namespace( # property names of Colorama.Fore
      debug = ('l_black', 'l_black'),
      info = ('l_white', 'l_white'),
      note = ('l_cyan', 'l_white'),
      warn = ('l_yellow', 'l_yellow'),
      error = ('l_red', 'l_red'),
    )
  ),

  Text = Namespace(
    LogIssuerTypes = Namespace(
      kernel = 'Kernel',
      plugin = 'Plugin',
    ),
    ErrorMessages = Namespace(
      dummy = 'Dummy error from {key}',
    )
  )
)
