from time import sleep
from datetime import datetime

class TpsMonitor:
  def __init__(self, tps):
    self.target = 1e6 / tps
    self.tps = 0
    self.newTpsReading = False
    self.ticks = 0
    self.lastTick = datetime.now()
    self.lastSecond = -1
    self.bilance = 0

  def setTarget(self, tps):
    self.target = 1e6 / tps

  def tick(self):
    self.newTpsReading = False
    self.ticks += 1
    now = datetime.now()
    if now.second != self.lastSecond:
      self.newTpsReading = True
      self.tps = self.ticks
      self.ticks = 0
      self.lastSecond = now.second
    # Slow down if necessary
    delta = now - self.lastTick
    elapsed = delta.seconds / 1e6 + delta.microseconds
    self.bilance += self.target - elapsed
    if self.bilance > 0: sleep(self.bilance / 1e6)
    self.lastTick = now
