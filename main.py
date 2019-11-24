import Pluginable as plg

if __name__ == '__main__':
  plg.Settings.Compiler.pluginDirectories = ['./Plugins/myplugs']
  prog = plg.Program()
  prog.preload()
  prog.run()
