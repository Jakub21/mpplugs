## Quick introduction to Pluginable
Pluginable can be used to create modular programs.


### About
- On program start-up `init` method of each plugin is executed
- Until program is closed `update` method is executed in loop
- Just before program exits `quit` method is called
- Plugins can issue events and have event handler methods assigned
- Each plugin runs in separate process so the only way to communicate is with events
- Code in Pluginable plugins may be considered unorthodox by some people, beware


### Installation
Pluginable, as of the day I'm writting this, is not available on PIP.
Download latest release from [here](https://github.com/Jakub21/Pluginable/releases)
and install it with command `python setup.py install`.


### Creating and starting demo program

Create main program file

File `./program.py` - this is where you configure your program and plugins
```python
import Pluginable as plg # Import Pluginable

if __name__ == '__main__':
  prog = plg.Program('MyBasicProgram') # Create program
  prog.updateSettings({ # Method for changing program settings
    'Compiler.pluginDirectories': ['./demoPlugins'], # Add plugins to your program
  })
  prog.preload() # Prepare plugins
  prog.run() # Create plugin instances in separate processes, exec init and start loop

```

Now create a `FirstDemo` plugin

File `./demoPlugins/FirstDemo/FirstDemo.py` - main file of `FirstDemo` plugin
```python

class FirstDemo(Plugin): # This is your plugin class, name must match file and directory names
  def init(self): # Note the lack of underscores, this is important
    super().init() # This is required
    Warn(self, 'Hello World!') # Add log entry (basically "print" but better)

  def update(self): # This gets called in loop (each call is a tick)
    super().update() # This also is required
    if not(self.__pluginable__.tick % 100): # Do this once every 100 ticks
      Debug(self, 'Another 100 ticks') # Add log

```

File `./demoPlugins/FirstDemo/Config.py` - configuration file for your plugin
```python
class Config:
  pass # This file is more useful in more advanced plugins
```

File `./demoPlugins/FirstDemo/Scope.py` - imports and globals
```python
pass # This one is also not useful in basic plugins but it has to exist
```

After you execute `program.py` this should write some stock logs but you also should be able to find your `Hello World!` log in yellow. Screen should soon fill up with `Another 100 ticks` calls in grey.

You can stop the program with standard `Ctrl-C`.

Pluginable has no limitation (or it was not found) on how many plugins you can add.
Just add directory where you store them to program settings and they should be loaded.
Note that you have to add parent directory of your plugin, not plugin itself.
Also creating folders that are not plugins in added directories may cause problems.


### Basic events demo

Events system is very useful in bigger programs. This is how to use them.
Before you start:
- Create another plugin by copying contents of `FirstDemo` to `SecondDemo`
- Rename `SecondDemo/FirstDemo.py` to `SecondDemo.py`
- In `SecondDemo.py` rename class `FirstDemo` to `SecondDemo`

Then paste this to your `FirstDemo.py`
```python
class FirstDemo(Plugin):
  def init(self):
    super().init()
    Warn(self, 'Hello World!')
    self.addEventHandler('DummyEvent', self.onDummy) # Add handler
    # any time there is event with id "DummyEventId" anywhere in the program
    # method onDummy will be called

  def update(self):
    super().update()
    # Do stuff...

  def onDummy(self, event):
    Info(self, f'First\'s onDummy {event.tick}') # Add log (white)

```

And this in `SecondDemo.py` instead of your current update method
```python
def update(self):
  super().update()
  tick = self.__pluginable__.tick
  if not(tick % 200):
    Event(self, 'DummyEvent', tick=tick) # Issue an event
    # Every handler anywhere in the program will be called
```

Each event can have multiple handlers, also in plugin that issues that event.
Event handlers are executed in the same process as plugin ticks.

Events accept keyword parameters that are stored as object properties.
Note that objects that are not pickable can not be passed (streams, buffers etc).


### Summary
There are many features not described here but this knowledge is sufficient
to create basic programs in Pluginable.
For details check other sections of this documentation.
