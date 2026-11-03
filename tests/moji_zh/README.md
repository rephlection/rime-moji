# `moji_zh` tests

Run the static configuration checks and, when the real librime tools are
available, the deployment/input integration test:

```sh
python3 -m unittest discover -s tests/moji_zh -v
```

The static test uses PyYAML. The integration test requires `RIME_DEPLOYER`,
`RIME_LUA_PLUGIN` (the `librime-lua` plugin), `RIME_LIBRARY` (the librime shared
library), and a C++ compiler (`g++` by default; override with `CXX`). If
`rime_api.h` is not in `/usr/include`, set `RIME_INCLUDE_DIR`. Make both runtime
library directories available through `LD_LIBRARY_PATH` as needed. Example:

```sh
RIME_DEPLOYER=/path/to/rime_deployer \
RIME_LUA_PLUGIN=/path/to/rime-plugins/librime-lua.so \
RIME_LIBRARY=/path/to/librime.so \
RIME_INCLUDE_DIR=/path/to/include \
LD_LIBRARY_PATH=/path/to/librime/lib:/path/to/lua/runtime/lib \
python3 -m unittest discover -s tests/moji_zh -v
```

The integration test creates an isolated data tree, deploys the actual schemas
and Lua modules with tiny fixture dictionaries, and sends keys through real
librime/librime-lua sessions. It checks Chinese pinyin candidate order and
commit, `-`/`=` paging, `ja`-prefix Japanese candidates, digit selection and
commit, partial-candidate selection followed by continued input, `zh_only`, and
the distinct left/right Shift paths.
Large dictionaries are replaced only inside the temporary test tree; repository
files and user data are not modified.
