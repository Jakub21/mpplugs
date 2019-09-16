from argparse import ArgumentParser as Parser
from _scriptUtils import *

class data:
  task = '''# Task {plugin}::{task}
class {task}(Task):
  def execute(self):
    super().execute()
    # write task code here
'''

if __name__ == '__main__':
  base = getBaseDir()

  parser = Parser()
  parser.add_argument('scope')
  parser.add_argument('plugin')
  parser.add_argument('task')
  args = parser.parse_args()
  scope = args.scope
  plugin = args.plugin
  task = args.task

  validate(scope)
  validate(plugin)
  validate(task)

  if task[0] != task[0].upper():
    print('First letter of the task name will be changed to upper case')
    task = task[0].upper() + task[1:]

  print(f'Creating task "{task}" of plugin "{scope}::{plugin}"')
  task = '_' + task

  try:
    with open(f'{base}/Plugins/{scope}/{plugin}/{task}.py', 'w', newline='\n') as f:
      f.write(data.task.format(plugin=plugin, task=task))
  except FileNotFoundError:
    print(f'Plugin {scope}::{plugin} was not found')
