from Pluginable.Namespace import Namespace

class Logger:
  def __init__(self, file, mode):
    self.logger = Namespace()
    file = file.replace('\\', '/')
    self.logger.file = '::'.join(file.split('/')[-2:])[:-3]
    self.logger.mode = mode

  def logError(self, *msg, **kwargs):
    print(f'[CRIT][{self.logger.file}]:', *msg, **kwargs)

  def logWarn(self, *msg, **kwargs):
    print(f'[WARN][{self.logger.file}]:', *msg, **kwargs)

  def logNote(self, *msg, **kwargs):
    print(f'[NOTE][{self.logger.file}]:', *msg, **kwargs)

  def logInfo(self, *msg, **kwargs):
    print(f'[INFO][{self.logger.file}]:', *msg, **kwargs)

  def logDebug(self, *msg, **kwargs):
    print(f'[DEBG][{self.logger.file}]:', *msg, **kwargs)
