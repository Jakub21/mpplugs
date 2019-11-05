from Pluginable import Program

if __name__ == '__main__':
  prog = Program()
  prog.config(
    loaderDirectories = ['myplugs'],
  )
  prog.preload()
  prog.run()
