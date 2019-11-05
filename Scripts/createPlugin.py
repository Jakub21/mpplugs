from argparse import ArgumentParser as Parser
from _scriptUtils import *

class data:
  scope = '''
from Pluginable import Plugin, Task, Event
'''
  config = '''
class Config:
  pass
'''
  main = '''
class {plugin}(Plugin):
  def init(self):
    super().init()

  def update(self):
    super().update()

  def quit(self):
    super().quit()
'''

if __name__ == '__main__':
  base = getBaseDir()

  parser = Parser()
  parser.add_argument('scope')
  parser.add_argument('plugin')
  args = parser.parse_args()
  scope = args.scope
  plugin = args.plugin

  validate(scope)
  validate(plugin)

  if plugin[0] != plugin[0].upper():
    print('First letter of the plugin plugin will be changed to upper case')
    plugin = plugin[0].upper() + plugin[1:]

  print(f'Creating plugin "{plugin}" in scope "{scope}"')

  # Create plugin directory
  ifnmkdir(f'{base}/Plugins/{scope}')
  try: mkdir(f'{base}/Plugins/{scope}/{plugin}')
  except FileExistsError:
    print(f'Plugin directory already exists, see Plugins/{scope}/{plugin}')
    fexit()

  # Create files
  with open(f'{base}/Plugins/{scope}/{plugin}/Scope.py', 'w', newline='\n') as f:
    f.write(data.scope)
  with open(f'{base}/Plugins/{scope}/{plugin}/Config.py', 'w', newline='\n') as f:
    f.write(data.config)
  with open(f'{base}/Plugins/{scope}/{plugin}/{plugin}.py', 'w', newline='\n') as f:
    f.write(data.main.format(plugin=plugin))

  print('Done')
