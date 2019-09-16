from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace

class Plugin(Logger):
  def __init__(self, prog):
    super().__init__(__file__, 'plugin')
    self.prog = prog
    self.tasks = Namespace()

  def init(self):
    self.logDebug(f'Plugin {self.key} inits')

  def update(self):
    pass

  def quit(self):
    self.logDebug(f'Plugin {self.key} quits')

  def __repr__(self):
    return f'<Plugin {self.key}>'
