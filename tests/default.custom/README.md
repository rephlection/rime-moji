# default.custom tests

Run the YAML/reference checks with:

```sh
python3 -m unittest discover -s tests/default.custom -v
```

To also exercise the configuration with librime's deployer, set `RIME_DEPLOYER`
to a `rime_deployer` executable and make its shared libraries available through
`LD_LIBRARY_PATH`:

```sh
RIME_DEPLOYER=/path/to/rime_deployer \
LD_LIBRARY_PATH=/path/to/librime/lib \
python3 -m unittest discover -s tests/default.custom -v
```

The integration test creates temporary user/shared/staging directories, uses
`refs/rime-prelude` as the base Rime configuration, runs `rime_deployer
--build`, and checks the compiled `default.yaml`. It does not modify user data.
