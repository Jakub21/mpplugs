## Crating Plugins

### Structure
Plugin consists of at least 3 files.
Those must be in the same directory and follow some naming rules.
Some of the code you put in them also must follow some naming rules.

1. Create directory and name it as you want. For guide purposes I will assume it's `MyPlugin`
1. In `MyPlugin` create 3 files: `MyPlugin.py`, `Config.py` and `Scope.py`
1. Leave `Scope.py` empty for now
1. Open `Config.py` and type
  ```python
  class Config: pass
  ```
1. Open `MyPlugin.py` and put the following code there
  ```python
  class MyPlugin(Plugin):
    def init(self):
      super().init()

    def update(self):
      super().update()

    def quit(self):
      super().quit()
  ```

Those steps create empty plugin that passes start-up tests.
It does not do anything yet.

### Scope file
This file is intented to contain all imports, global definitions etc.
It is always loaded into program first.
Whatever you define in here is available in whole plugin, including the Config.

### Config
Data from this class is copied to `cnf` property of main plugin class for easy access.

To add config entries, simply add properties to `Config` class.
You can also create nested configs by creating more classes inside `Config`.

Contents of this class can be easily changed on program start-up from
[executable file](docs/Executable.md#Configuring-plugins).

```python
class Config:
  simpleEntry = 3
  desc = 'Any variable type is valid'
  class NestedStuff:
    anotherEntry = False
```

It is not recommended to add code outside `Config` class in this file.

### Plugin-named main file
This is main plugin file where most things happen.

How it works:
- `init` method is called once when plugin starts.
- `update` method is called in loop until program stops.
- `quit` method is called once just before program stops.

It is not recommended to add code outside main class in this file.

### Program init
TODO: describe `Program.onProgramInit` method

### Additional files
You can create more files and add any code in them.
Those are loaded just after `Scope` file so their content is also available in whole plugin.
