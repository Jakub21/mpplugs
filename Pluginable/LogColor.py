from Pluginable.Namespace import Namespace
from os import name as osName, system

if osName == 'nt': system('color')

_prefix = '\033['
_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
_lfg = {key: _prefix + str(index+90) + 'm' for index, key in enumerate(_order)}
_dfg = {key: _prefix + str(index+30) + 'm' for index, key in enumerate(_order)}
_lbg = {key: _prefix + str(index+100) + 'm' for index, key in enumerate(_order)}
_dbg = {key: _prefix + str(index+40) + 'm' for index, key in enumerate(_order)}

LogColor = Namespace( className = 'LogColor',
  rst = _prefix + '0m',
  inv = _prefix + '7m',
  fg = Namespace(**{f'l_{k}':v for k,v in _lfg.items()},
    **{f'd_{k}':v for k,v in _dfg.items()}),
  bg = Namespace(**{f'l_{k}':v for k,v in _lbg.items()},
    **{f'd_{k}':v for k,v in _dbg.items()}),
)
