import sys

from Pluginable.Namespace import Namespace
Levels = Namespace(Debug = 0, Info = 1, Note = 2, Warn = 3, Critical = 4)

class StreamOutput:
  def __init__(self, stream, colored=False, minLevel=Levels.Debug, maxLevel=Levels.Critical, enabled=True):
    self.stream = stream
    self.colored = colored
    self.minLevel, self.maxLevel = minLevel, maxLevel
    self.enabled = enabled

  def write(self, data):
    self.stream.write(data)
    self.stream.flush()

class FileOutput(StreamOutput):
  def __init__(self, filename, colored=False, minLevel=Levels.Debug, maxLevel=Levels.Critical, enabled=True):
    with open(filename, 'a') as file: pass
    self.filename = filename

  def write(self, data):
    with open(self.filename) as file:
      file.write(data)

stdout = StreamOutput(sys.stdout, colored=True, maxLevel=Levels.Note)
stderr = StreamOutput(sys.stderr, colored=True, minLevel=Levels.Warn)
