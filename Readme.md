## MP Plugs
Universal Python Framework.

MPPlugs helps to create modular applications with setup + loop structure common in microcomputer and GUI programming.

### Documentation
Documentation is available [here](https://jakub21.github.io/mpplugs/)

### Latest stable version
[Release v0.4](https://github.com/Jakub21/mpplugs/releases/latest)

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
