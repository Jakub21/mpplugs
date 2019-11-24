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
# from Pluginable import Debug, Info, Note, Warn, Error
from Pluginable import Settings

# Plugin code

'''
    )
  ),

  Logger = Namespace(
    timeFormat = '24h',
    timeRelative = False,
    logOutputs = [stdout, stderr],
    colors = Namespace( # property names of Colorama.Fore
      debug = ('LIGHTBLACK_EX', 'LIGHTBLACK_EX'),
      info = ('WHITE', 'WHITE'),
      note = ('LIGHTCYAN_EX', 'WHITE'),
      warn = ('LIGHTYELLOW_EX', 'LIGHTYELLOW_EX'),
      error = ('LIGHTRED_EX', 'LIGHTRED_EX'),
    )
  ),

  Text = Namespace(
    ErrorMessages = Namespace(
      dummy = 'Dummy error from {key}',
    )
  )
)
