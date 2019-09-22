from Pluginable.Logger import Logger

class Task(Logger):
  def __init__(self, *args, **kwargs):
    super().__init__((self.plugin.scope, self.plugin.key, self.key), 'task')
    self.args = args
    self.kwargs = kwargs

  def execute(self):
    if self.plugin.prog.settings.logTasksExecution:
      self.logDebug(f'Executing task {self.plugin.key}.{self.key}')

  def __repr__(self):
    return f'<Task {self.plugin.key}.{self.key}>'
