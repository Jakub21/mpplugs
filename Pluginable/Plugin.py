from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace

class Plugin(Logger):
  def __init__(self, scope, key, logLock):
    self.scope, self.key = scope, key
    super().__init__((self.scope, self.key), 'plugin', logLock)
    self.tick = 0

  def init(self):
    self.INITIALIZED = True

  def update(self):
    self.tick += 1

  def quit(self):
    self.logInfo(f'Plugin {self.key} quits')

  def __repr__(self):
    return f'<Plugin {self.key}>'
