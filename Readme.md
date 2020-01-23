## Pluginable
Universal Python Framework.

Pluginable helps to create modular applications with setup + loop structure common in microcomputer and GUI programming.

### Documentation
- [Quick introduction](docs/QuickIntro.md) - Everything you need to know to get started
- [Executable file](docs/Executable.md) - Guide on writing start-up files
- [Create a plugin](docs/CreatePlugin.md) - Guide on creating plugins
- [List of program settings](docs/Settings.md) - List of settings in Program class
- [Full API](docs/API.md) - All classes and methods listed and described

### Latest stable version
[Release v0.4](https://github.com/Jakub21/Pluginable/releases/tag/v0.4)

**Features**
- init + loop approach
- utilizes multiprocessing (each plugin runs in a separate process)
- supports events system (plugins can communicate with each other this way)
- unified plugins I/O (allows GUI generators etc)

**New in this version**
- Changed how excpetions are displayed. Useful during plugin creation, debug and testing
- Created documentation
- Other minor improvements

### Framework applications
This framework was tested with the following packages: `PyGame`, `TkInter`, `socket`.
