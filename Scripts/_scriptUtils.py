from os import mkdir, path

def ifnmkdir(d):
  try: mkdir(d)
  except FileExistsError: pass

def fexit():
  print('Failure')
  exit()

def validate(val):
  digits = [chr(l) for l in range(ord('0'), ord('9'))]
  lower = [chr(l) for l in range(ord('a'), ord('z'))]
  upper = [chr(l) for l in range(ord('A'), ord('Z'))]
  for c in val:
    if (c not in digits) and (c not in lower) and (c not in upper) and (c != '_'):
      print(f'Only alphanumeric chars and underscores are allowed ({c})')
      fexit()
  if val[0] in digits:
    print('Value can not start with a digit')
    fexit()
  if len(val) < 3:
    print('Value length must be at least 3')
    fexit()

def getBaseDir():
  return '/'.join(path.abspath(__file__).replace('\\', '/').split('/')[:-2])
