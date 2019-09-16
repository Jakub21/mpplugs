## Pluginable
Pluginable is a framework for Python applications with text or graphical user interface.

Pluginable helps to create modular applications with setup + loop idea common for example in microcomputer or GUI programming.

### Usage

#### Installation
In current version Pluginable is not an installable package. Instead to use it put source files in this way:
```
YourProject/ (root of this repository becomes root of your project, rename it as you wish)
  |- Pluginable/
    |- __init__.py
    |- source files...
  |- Scripts/
    |- createPlugin.py (use this script to create new plugins)
    |- createTask.py (use this script to create new task inside a plugin)
    |- source files...
  |- Plugins/ (your plugins go here)
    |- dummy
  |- Readme.md (this file)
```

#### Creating plugins
Plugin is a directory with a few files that must follow strict naming rules. Those files must contain classes that also are a subject to naming rules. To avoid learning those rules you can use scripts I've put in `Scripts/` directory.

#### Plugins structure
Plugins consist of `core`, `scope`, `config`, `tasks` and `helpers`.
- `Core`is a main class of plugin that contains method that are called at program start, at program tick and when program ends. Core is also used to manage tasks, helpers and it is where config lives after plugin is loaded.
- `Scope` is a file with imports and variable definitions. Those variables can be accessed anywhere in plugin, helpers and tasks code.
- `Config` is a class with plugin configuration. It can be accessed as a property of core plugin object `cnf`.
- `Tasks` are objects that contain a method that can be executed as a program task. Task objects are pushed into a program tasks queue when created and their `execute` method gets called when they are in the queue head and get popped.
- `Helpers` are regular classes that can be accessed anywhere in plugin code.

#### How Pluginable program works
When program is started first plugins are loaded. Plugins are grouped in scopes so you can enable or disable plugins score anytime you want in your `main.py` file. Then plugins are initialized (method `init` of plugin core is called now).

If all plugins were initalized successfully main loop is started. Main loop runs infinitely and in each iteration it calls `update` method of each plugin.

If there is a task in the queue it is popped and executed. You can control how many tasks are executed per loop iteration.

When loop is broken by user, task, error or interruption, `quit` methods of all plugins are called and then program `run` method returns. What happens then depends on your `main.py` contents but usually script ends.

#### Executing tasks
To add task to the task queue call `pushTask` method of the program. You can access the program object in plugins by using `prog` property. Task classes are in `tasks` namespace that also is member of a plugin core. Note that `pushTask` accepts task instances, not classes. Example: `self.prog.pushTask(self.tasks.myTask())`.

### Applications
Early versions of this software were tested with plugins that used the following packages.
- `PyGame`
- `TkInter`
- `socket`
