from Pluginable.Logger import Logger
from Pluginable.Namespace import Namespace

class Plugin(Logger):
  DEPENDENCIES = []
  INITIALIZED = False
  def __init__(self, prog):
    super().__init__(__file__, 'plugin')
    self.prog = prog
    self.tasks = Namespace()

  def init(self):
    for key in self.DEPENDENCIES:
      try: dependency = self.prog.plugins[key]
      except:
        raise ValueError(f'Plugin {self.key} depends on {key}')
      if not dependency.INITIALIZED:
        raise ValueError(f'Dependency {dependency.key} must be initialized first')
    self.INITIALIZED = True
    self.logDebug(f'Plugin {self.key} inits')

  def update(self):
    pass

  def quit(self):
    self.logDebug(f'Plugin {self.key} quits')

  def __repr__(self):
    return f'<Plugin {self.key}>'
