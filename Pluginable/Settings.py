from Pluginable.Namespace import Namespace
from Pluginable.Event import Event
from Pluginable.LogOutputs import stdout, stderr
from datetime import datetime

Settings = Namespace(

  StartTime = datetime.now(),

  Kernel = Namespace(
    MaxProgramTicksPerSec = 128,
    MaxExecutorTicksPerSec = 128,
    PluginAwaitProgramInit = True,
    MaxPluginCleanupDuration = 0.3,
    AutoAddTickToPluginOutputs = False,
    AutoAddTpsToPluginOutputs = False,
  ),

  Compiler = Namespace(
    cacheDirectory = '_PluginableCache',
    pluginDirectories = [],
    omitPlugins = [],
    data = Namespace(
      compilationPrefix = '''
# File compiled by pluginable, any edits will be automatically overwritten
from Pluginable import Plugin, Settings, Namespace
from Pluginable import PluginEvent as Event
from Pluginable.Logger import Debug, Info, Note, Warn, Error

# Plugin code

'''
    ),
  ),

  Logger = Namespace(
    appendOriginalTraceback = False,
    enablePluginTps = False,
    timeFormat = '24h',
    timeMode = 'absolute',
    timePrefix = Namespace(
      absolute = '@',
      relative = 'T+',
    ),
    logOutputs = [stdout, stderr],
    colors = Namespace( # level = (timeColor, prefixColor, messageColor)
      debug = ('l_magenta', 'l_black', 'l_black'),
      info = ('l_magenta', 'l_white', 'l_white'),
      note = ('l_cyan', 'l_cyan', 'l_white'),
      warn = ('l_yellow', 'l_yellow', 'l_yellow'),
      error = ('l_red', 'l_red', 'l_red'),
    ),
  ),

  Text = Namespace(
    LogIssuerTypes = Namespace(
      kernel = 'Kernel',
      plugin = 'Plugin',
    ),
  ),

  Custom = Namespace(), # Fill with Program.customSettings
)
