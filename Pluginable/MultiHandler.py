''' Utility functions for handling mulltiprocessing queue errors
Program that otherwise works properly
starts throwing tons of errors once it starts closing

When better solution to this problem is found those functions should be replaced
with functions they are wrapping
'''

def push(queue, item):
  try: queue.put(item)
  except (BrokenPipeError, EOFError): pass

def pop(queue):
  return queue.get()

def empty(queue):
  try: return queue.empty()
  except (BrokenPipeError, EOFError): return True

def get(variable):
  try: return variable.value
  except (BrokenPipeError, EOFError): return None

def set(variable, value):
  try: variable.value = value
  except (BrokenPipeError, EOFError): pass
