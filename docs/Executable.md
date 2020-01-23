## Program executable
This file is used to start the program.
Here you can link plugins, configure program etc.

### Basic file
This is minimal code required to start a Pluginable program.
```python
import Pluginable as plg

if __name__ == '__main__':
  prog = plg.Program('DummyProgram')
  prog.updateSettings({
    'Compiler.pluginDirectories': ['./myPlugins'],
  })
  prog.preload()
  prog.run()
```
You can replace program name (`DummyProgram`) with any string that follows variable naming rules.

`./myPlugins` is directory in which you store plugins.
You can add add multiple directories by adding them to the list.
This config is required to start the program.

### Settings
If you want to change program settings just add an item in dictionary passed to `updateSettings`
like so
```python
prog.updateSettings({
  'Kernel.PluginAwaitProgramInit': True,
  'Compiler.pluginDirectories': ['./myPlugins'],
  'Logger.enablePluginTps': True,
})

```
For full list of available settings see [Settings section](docs/Settings.md)

### Custom settings
You can also add custom settings with `customSettings` method.
Custom settings are added to `Custom` property of Settings.
This means their dot-joined-path is always prefixed with `Custom.`.
For example
```python
prog.customSettings({
  'myCustomSetting': 128,
  'anotherCustom': 'Hello',
})
```
adds settings `Custom.myCustomSetting` and `Custom.anotherCustom`.

### Configuring plugins
There is a built-in method for changing plugin configuration from executable file.
Note that it can only be used between `preload` and `run` method calls.

```python
prog.configPlugin('PluginToConfigure', {
  'simpleEntry': 12,
  'NestedStuff.anotherEntry': True,
})

```
Creating plugin configs is described in [Plugin config section](docs/PluginConfig.md)
