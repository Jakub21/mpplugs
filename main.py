# Example usage of Pluginable
# See Readme for more info

from Pluginable import Program

if __name__ == '__main__':
  program = Program()
  program.config('tasksPerTick', 3)
  program.plgLoader.addDirectory('myplugs')
  program.initPlugins()
  program.run()
