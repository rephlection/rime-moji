# `moji_ja` tests

Run the schema deployment smoke test and the librime-lua input integration test:

```sh
python3 -m unittest discover -s tests/moji_ja -v
```

The deployment test requires `RIME_DEPLOYER`. The Lua integration test is
optional and also requires `RIME_LUA_PLUGIN` (the `librime-lua` plugin),
`RIME_LIBRARY` (the librime shared library), and a C++ compiler (`g++` by
default; override with `CXX`). If `rime_api.h` is not in `/usr/include`, set
`RIME_INCLUDE_DIR`. Make the runtime libraries for librime and librime-lua
available through `LD_LIBRARY_PATH` as needed. Example:

```sh
RIME_DEPLOYER=/path/to/rime_deployer \
RIME_LUA_PLUGIN=/path/to/rime-plugins/librime-lua.so \
RIME_LIBRARY=/path/to/librime.so \
RIME_INCLUDE_DIR=/path/to/include \
LD_LIBRARY_PATH=/path/to/librime/lib:/path/to/lua/runtime/lib \
python3 -m unittest discover -s tests/moji_ja -v
```

The Lua test creates an isolated temporary Rime data tree, deploys it, loads
the Lua plugin, then sends romaji sequences through real Rime sessions. It
checks `konnichiha`, `nn`, `nni`, `nnya`, and `n'`. The large Japanese
vocabulary tables are replaced with tiny test dictionaries; the actual
`moji_ja` schema, Lua modules, and romaji dictionary are used. No user data or
tracked files are modified.
