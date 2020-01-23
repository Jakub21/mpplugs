List of classes, their methods and properties. Work in progress.

# Main process classes

### `Program`
**Inherits from** [LogIssuer](#LogIssuer)

**Properties**
- bool `quitting` - Flag changed to True when quit procedure starts
- int `tick` - How many ticks have passed since program start
- dict `eventHandlers` - Stores lists of handlers assigned to event ids
- [Compiler](#Compiler) `compiler` - Assigned compiler instance
- [TpsMonitor](#TpsMonitor) `tpsMon` - Assigned TPS Monitor instance. Monitors and controls ticks/sec of main process.

**Methods**
- `customSettings(dict data)` - Add custom settings entries
- `updateSettings(dict data)` - Update program settings
- `configPlugin(str pluginKey, dict data)` - Change plugin config
- `preload()` - Prepare cache and check for errors. Must be called before starting the program.
- `run()` - Use to start the program.


### `Compiler`
**Inherits from** [LogIssuer](#LogIssuer)

**Properties**
- [Program](#Program) `prog` - Program instance compiler is assigned to

**Methods**
- `compile()` - Compile code of all plugins added in settings and save to cache.
- `load()` - Load all plugins from cache.



# Plugin process classes

### `Plugin`
**Inherits from** [LogIssuer](#LogIssuer)

**Properties**
- [Namespace](#Namespace) `__pluginable__` - Namespace used to separate pluginable properties from plugin-specific ones.
  - str `key` - Plugin key, used as unique identifier.
  - int `tick` - How many ticks have passed since plugin init.
- [Executor](#Executor) `executor` - Assigned executor instance. (Property added by executor itself)

**Methods**
- `init()` - Method automatically called to initialize plugin.
- `update()` - Method automatically called in loop, after init, until program quits.
- `quit()` - Method automatically called when program stops.
- `addInputNode(str key, callable handler, *parameterKeys)` - Call this in `init` to create plugin input node.
- `addEventHandler(str eventKey, callable handler)` - Call this in `init` to create event handler.
- `stopProgram()` - Call this anywhere in plugin to exit the program (will perform cleanup).
- `setPluginOutputs(**data)` - Call this to update outputs state.


### `Executor`
**Inherits from** [LogIssuer](#LogIssuer)

**Properties**
- [Plugin](#Plugin) `plugin` - Plugin this executor is assigned to
- str `key` - Identifier of plugin this executor is assigned to.
- bool `initialized` - Flag changed to True when plugin initialization is successful.
- bool `programInitDone` - Flag changed to True when all plugins have finished initialization.
- [TpsMonitor](#TpsMonitor) `tpsMon` - Assigned TPS Monitor instance. Monitors and controls ticks/sec of assigned plugin.
- bool `quitting` - Flag changed to True when program quits.
- <multiprocessing.manager.Value-int> `quitStatus` - When value is changed to 1 plugin force stops.



# Utility classes

### `TpsMonitor`
**Properties**
- int `tps` - Last TPS (ticks per second) reading
- bool `newTpsReading` - After last tick `tps` property was updated

**Methods**
- `setTarget(tps)` - Set target TPS. If `tick` method is called more frequently
  delay will be enabled to slow down loop that calls it.
- `tick()` - Call this method every tick


### `LogIssuer`
**Properties**
- [Namespace](#Namespace) `_logger_data`
  - str `type` - Issuer type. Valid values are `kernel` and `plugin`.
    This property affects issuer prefix in logs.
  - str `path` - Issuer name or path.


### `StreamOutput`
**Properties**
- stream `stream` - Stream to write logs to
- bool `colored` - If set to True colors will be applied
- int `minLevel` - Minimum log level to write to this output
- int `maxLevel` - Maximumu log level to write to this output
- bool `enabled` - If set to False no logs will be written

**Methods**
- `write(str data)` - Use to write data to stream


### `FileOutput`
**Inherits from** [StreamOutput](#StreamOutput)

**Properties**
- str `filename` - Name of file to write logs to


### `Event`
**Properties**
- str `issuer` - Name of entity that issued this event
- str `id` - ID of this event. Triggers handlers assigned to this ID.

**Methods**
- `getArgs()` - Return event kwarg data in form of a dictionary


### `Namespace`
**Methods**
- `items()` - Works just like `dict.items`
- `keys()` - Works just like `dict.keys`
- `values()` - Works just like `dict.values`
- `toString(int indent=0, str className='Namespace')` - Return string representation
  of this Namespace



# Exceptions

### `PluginableException`
All exceptions inherit from this one.

### `CompilerError`
All compiler exceptions inherit from this one.
#### `CompilerNoDirectoryError`
Raised when directory added in settings does not exist.
#### `CompilerNoDirsAddedError`
Raised when no plugin directories were added in settings.
#### `CompilerMissingFileError`
Raised when plugin lacks required file (`{PluginName}.py`, `Config.py`, `Scope.py`)
#### `CompilerMissingClassError`
Raised when plugin lacks required class (`class {PluginName}`, `class Config`)

### `PluginError`
All plugin exceptions inherit from this one.

### `PluginStartupError`
The following exceptions inherit from this one.
##### `PluginSyntaxError`
Raised when there is a syntax error in plugin code.
##### `PluginLoadError`
Raised when an error occurs at preload (during plugin code execution).
Indicates error outside any functions.
##### `PluginConfigError`
Raised when attempted to change plugin config entry that does not exist.

### `PluginRuntimeError`
The following exceptions inherit from this one.
##### `PluginInitError`
Raised when an error occurs during plugin init.
##### `PluginTickError`
Raised when an error occurs during plugin tick (method `update`).
##### `PluginEventError`
Raised when an error occurs while handling event.
