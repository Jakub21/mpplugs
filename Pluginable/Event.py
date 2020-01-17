import Pluginable.MultiHandler as mh
from traceback import format_tb

class Event:
  def __init__(self, issuer, id, **data):
    self.issuer = issuer
    self.id = id
    self.__dict__.update(data)

  def getArgs(self):
    return {k:v for k, v in self.__dict__.items() if k != 'id'}

  def __repr__(self):
    args = ', '.join([f'{k}={v}' for k, v in self.getArgs().items()])
    return f'<Event "{self.id}" {{{args}}}>'

class ErrorEvent:
  @staticmethod
  def exceptionToDict(exception):
    try: noTraceback = exception.noTraceback
    except AttributeError: noTraceback = False
    result = {
      'name': exception.name,
      'info': exception.info,
    }
    try: result['originalTraceback'] = exception.originalTraceback
    except AttributeError: pass
    return result


class KernelEvent(Event):
  def __init__(self, id, **kwargs):
    super().__init__('_Kernel_', id, **kwargs)

class KernelExcEvent(KernelEvent, ErrorEvent):
  def __init__(self, critical, exception):
    super().__init__('KernelError', critical=critical,
      **self.exceptionToDict(exception))


class ExecutorEvent(Event):
  def __init__(self, issuer, id, **kwargs):
    super().__init__(issuer.key, id, **kwargs)
    mh.push(issuer.evntQueue, self)

class ExecutorExcEvent(ExecutorEvent, ErrorEvent):
  def __init__(self, issuer, critical, exception):
    super().__init__(issuer, 'PluginError', critical=critical,
      **self.exceptionToDict(exception))


class PluginEvent(Event):
  def __init__(self, issuer, id, **kwargs):
    super().__init__(issuer.__pluginable__.key, id, **kwargs)
    mh.push(issuer.executor.evntQueue, self)

class PluginExcEvent(PluginEvent, ErrorEvent):
  def __init__(self, issuer, critical, exception):
    super().__init__(issuer, 'PluginError', critical=critical,
      **self.exceptionToDict(exception))
