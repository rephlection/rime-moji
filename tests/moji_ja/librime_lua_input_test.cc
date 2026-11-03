#include <rime_api.h>

#include <dlfcn.h>
#include <cstdio>
#include <cstring>

int main(int argc, char** argv) {
  if (argc < 7 || (argc - 5) % 2 != 0) {
    std::fprintf(stderr, "usage: %s plugin shared user staging sequence expected [... ]\n", argv[0]);
    return 2;
  }
  void* plugin = dlopen(argv[1], RTLD_NOW | RTLD_GLOBAL);
  if (!plugin) {
    std::fprintf(stderr, "failed to load librime-lua: %s\n", dlerror());
    return 3;
  }

  RimeApi* api = rime_get_api();
  RimeTraits traits = {};
  RIME_STRUCT_INIT(RimeTraits, traits);
  traits.shared_data_dir = argv[2];
  traits.user_data_dir = argv[3];
  traits.staging_dir = argv[4];
  traits.app_name = "rime.moji.lua.test";
  traits.log_dir = "";
  const char* modules[] = {"default", "lua", nullptr};
  traits.modules = modules;
  api->setup(&traits);
  api->initialize(&traits);

  int result = 0;
  for (int i = 5; i + 1 < argc; i += 2) {
    RimeSessionId session = api->create_session();
    if (!session || !api->select_schema(session, "moji_ja")) {
      std::fprintf(stderr, "failed to create moji_ja session\n");
      result = 4;
      break;
    }
    api->set_option(session, "ascii_mode", False);
    if (!api->simulate_key_sequence(session, argv[i])) {
      std::fprintf(stderr, "failed to process key sequence: %s\n", argv[i]);
      result = 5;
    } else {
      const char* input = api->get_input(session);
      std::printf("%s => %s\n", argv[i], input ? input : "<null>");
      if (!input || std::strcmp(input, argv[i + 1]) != 0) {
        std::fprintf(stderr, "expected %s => %s\n", argv[i], argv[i + 1]);
        result = 10;
      }
    }
    api->destroy_session(session);
    if (result) break;
  }

  api->finalize();
  dlclose(plugin);
  return result;
}
