
class Queue:
  '''Queue class implementation based in list'''
  def __init__(self):
    self.elements = []

  def push(self, element):
    self.elements.append(element)

  def pop(self):
    element = self.elements[0]
    self.elements = self.elements[1:]
    return element

  def reset(self):
    self.elements = []

  def __len__(self):
    return len(self.elements)
