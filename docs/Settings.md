## List of program settings
Change with `updateSettings` method of `Program` class.

See `Pluginable/Settings.py` for defaults.

### Namespace `Kernel`

- `Kernel.MaxProgramTicksPerSec` (int) Maximum amount of updates per second in program's main process
- `Kernel.MaxExecutorTicksPerSec` (int) Maximum amount of updates per second plugins precesses
- `Kernel.PluginAwaitProgramInit` (bool) If True: plugins will not start ticking until init method of all plugins return; if False: plugins will start ticking as soon as their individual init methods return
- `Kernel.MaxPluginCleanupDuration` (float) [seconds] Maximum duration of plugin cleanup. After this time plugin processes are force closed.
- `Kernel.AutoAddTickToPluginOutputs` (bool) If True: Tick number will be automatically added to plugin outputs (in setPluginOutputs method)
- `Kernel.AutoAddTpsToPluginOutputs` (bool) If True: Latest ticks/sec reading will be automatically added to plugin outputs (in setPluginOutputs method)

### Namespace `Compiler`

- `cacheDirectory` (str) Compiled plugins code is stored on a disk. Name of the directory plugins are in is program name prefixed with this variable.
- `pluginDirectories` ([str]) Compiler will load plugins from those directories
- `omitPlugins` ([str]) Plugins with those keys will not be loaded

It is not recommended to change settings that start with `Compiler.data`.
Those will not be described.

### Namespace `Logger`

- `appendOriginalTraceback` (bool) Pluginable exceptions are often raised as a result of handling another exception. Setting this to True will enable logging traceback of the original exception.
- `enablePluginTps` (bool) If True: Log ticks/sec reading of each plugin every second
- `timeFormat` (str choice: `24h`, `12h`) Changes time format in logs
- `timeMode` (str choice: `absolute`, `relative`) Toggles relative / absolute time in logs
- `timePrefix`
  - `absolute` (str) Prefix added before time in `absolute` mode
  - `relative` (str) Prefix added before time in `relative` mode
- `logOutputs` ([Pluginable.StreamOutput, Pluginable.FileOutput]) Logger writes to those outputs
- `colors`
  - `debug` ((str,str,str)) Tuple of 3 color codes. 1st is time color, 2nd is issuer color, 3rd is message color. Available codes: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`. Add `l_` prefix for light version of the color.
  - `info` ((str,str,str)) see up ^
  - `note` ((str,str,str)) see up ^
  - `warn` ((str,str,str)) see up ^
  - `error` ((str,str,str)) see up ^

### Namespace `Text`

- `LogIssuerTypes` Text added as issuer prefix
  - `kernel` To Pluginable logs
  - `plugin` To plugin logs
