from Pluginable.Logger import Logger

class Task(Logger):
  def __init__(self):
    super().__init__(__file__, 'task')

  def execute(self):
    self.logDebug(f'Executing task {self.plugin.key}.{self.key}')

  def __repr__(self):
    return f'<Task {self.plugin.key}.{self.key}>'
