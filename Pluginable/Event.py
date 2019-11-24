
class Event:
  def __init__(self, issuer, id, **data):
    self.issuer = issuer
    self.id = id
    self.__dict__.update(data)

  def getArgs(self):
    return {k:v for k, v in self.__dict__.items() if k != 'id'}

  def __repr__(self):
    args = ', '.join([f'{k}={v}' for k, v in self.getArgs()])
    return f'<Event "{self.id}" {{{args}}}>'


class StockEvent(Event):
  def __init__(self, id, **kwargs):
    super().__init__(id, '<Kernel>' **kwargs)


class ExecutorEvent(Event):
  def __init__(self, issuer, id, **kwargs):
    super().__init__(issuer.plugin.key, id, **kwargs)
    issuer.evntQueue.put(self)


class PluginEvent(Event):
  def __init__(self, issuer, id, **kwargs):
    super().__init__(issuer.key, id, **kwargs)
    issuer.executor.evntQueue.put(self)
