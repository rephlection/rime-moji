#include <rime_api.h>

#include <dlfcn.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {

int Fail(const std::string& message, int code) {
  std::fprintf(stderr, "FAIL: %s\n", message.c_str());
  return code;
}

RimeSessionId NewSession(RimeApi* api, bool japanese = true) {
  RimeSessionId session = api->create_session();
  if (!session || !api->select_schema(session, "moji_zh")) return 0;
  api->set_option(session, "ascii_mode", False);
  api->set_option(session, "zh_ja", japanese ? True : False);
  return session;
}

bool InputIs(RimeApi* api, RimeSessionId session, const char* expected) {
  const char* input = api->get_input(session);
  return input && std::strcmp(input, expected) == 0;
}

bool ReadMenu(RimeApi* api, RimeSessionId session, std::vector<std::string>* texts,
              int* page_no = nullptr, int* page_size = nullptr,
              int* highlighted = nullptr) {
  RimeContext context = {};
  RIME_STRUCT_INIT(RimeContext, context);
  if (!api->get_context(session, &context)) return false;
  if (texts) {
    texts->clear();
    for (int i = 0; i < context.menu.num_candidates; ++i) {
      const char* text = context.menu.candidates[i].text;
      texts->emplace_back(text ? text : "");
    }
  }
  if (page_no) *page_no = context.menu.page_no;
  if (page_size) *page_size = context.menu.page_size;
  if (highlighted) *highlighted = context.menu.highlighted_candidate_index;
  api->free_context(&context);
  return true;
}

bool Has(const std::vector<std::string>& values, const char* value) {
  for (const auto& candidate : values) {
    if (candidate == value) return true;
  }
  return false;
}

bool ReadCommit(RimeApi* api, RimeSessionId session, std::string* text) {
  RimeCommit commit = {};
  RIME_STRUCT_INIT(RimeCommit, commit);
  if (!api->get_commit(session, &commit)) return false;
  *text = commit.text ? commit.text : "";
  api->free_commit(&commit);
  return true;
}

bool CommitAndRead(RimeApi* api, RimeSessionId session, std::string* text) {
  if (!api->commit_composition(session)) return false;
  return ReadCommit(api, session, text);
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 5) {
    std::fprintf(stderr, "usage: %s lua_plugin shared user staging\n", argv[0]);
    return 2;
  }
  void* plugin = dlopen(argv[1], RTLD_NOW | RTLD_GLOBAL);
  if (!plugin) return Fail(dlerror(), 3);

  RimeApi* api = rime_get_api();
  RimeTraits traits = {};
  RIME_STRUCT_INIT(RimeTraits, traits);
  traits.shared_data_dir = argv[2];
  traits.user_data_dir = argv[3];
  traits.staging_dir = argv[4];
  traits.app_name = "rime.moji.zh.input.test";
  traits.log_dir = "";
  const char* modules[] = {"default", "lua", nullptr};
  traits.modules = modules;
  api->setup(&traits);
  api->initialize(&traits);

  int result = 0;
  {
    // Verify basic pinyin candidates retain dictionary weight order and commit.
    RimeSessionId session = NewSession(api);
    if (!session) {
      result = Fail("create moji_zh session", 4);
    } else if (!api->simulate_key_sequence(session, "ba")) {
      result = Fail("type Chinese pinyin ba", 5);
    } else {
      std::vector<std::string> candidates;
      if (!ReadMenu(api, session, &candidates) || candidates.size() < 2 ||
          candidates[0] != "把" || candidates[1] != "吧") {
        result = Fail("ba candidates should follow the test dictionary weights", 6);
      } else if (!api->select_candidate(session, 1)) {
        result = Fail("select second Chinese candidate", 7);
      } else {
        std::string commit;
        if (!CommitAndRead(api, session, &commit) || commit != "吧")
          result = Fail("commit selected Chinese candidate", 8);
      }
    }
    if (session) api->destroy_session(session);
  }

  if (!result) {
    // Verify the project's default minus/equal paging bindings reach selector.
    RimeSessionId session = NewSession(api);
    if (!session || !api->simulate_key_sequence(session, "ba")) {
      result = Fail("prepare Chinese paging menu", 9);
    } else {
      int before = -1, after_down = -1, after_up = -1, page_size = 0;
      if (!ReadMenu(api, session, nullptr, &before, &page_size) || page_size < 2 ||
          !api->process_key(session, '=', 0) ||
          !ReadMenu(api, session, nullptr, &after_down) || after_down == before ||
          !api->process_key(session, '-', 0) ||
          !ReadMenu(api, session, nullptr, &after_up) || after_up != before) {
        result = Fail("minus/equal should page through Chinese candidates", 10);
      }
    }
    if (session) api->destroy_session(session);
  }

  if (!result) {
    // Verify the mounted Japanese processor/translator, digit selection, and commit.
    RimeSessionId session = NewSession(api);
    if (!session || !api->simulate_key_sequence(session, "jaa")) {
      result = Fail("type Japanese prefix sequence jaa", 11);
    } else {
      std::vector<std::string> candidates;
      if (!InputIs(api, session, "jaあ") || !ReadMenu(api, session, &candidates) ||
          candidates.size() < 2 || !Has(candidates, "あ")) {
        result = Fail("Japanese prefix should produce kana candidates", 12);
      } else {
        const std::string expected = candidates[1];
        const int digit_handled = api->process_key(session, '2', 0);
        std::string commit;
        if (!digit_handled || !ReadCommit(api, session, &commit) || commit != expected) {
          result = Fail("ASCII digit should select and commit the second Japanese candidate", 13);
        }
      }
    }
    if (session) api->destroy_session(session);
  }

  if (!result) {
    // A dictionary candidate covering only あ must leave the い tail active.
    // Its Kanji text also verifies that recognizer keeps the mounted tag after
    // partial selection, so the remaining Japanese translator can offer 愛.
    RimeSessionId session = NewSession(api);
    if (!session || !api->simulate_key_sequence(session, "jaai")) {
      result = Fail("type Japanese input with a partial-candidate boundary", 21);
    } else {
      std::vector<std::string> candidates;
      if (!InputIs(api, session, "jaあい") ||
          !ReadMenu(api, session, &candidates) || !Has(candidates, "亜")) {
        result = Fail("Japanese test dictionary should offer partial candidate 亜", 22);
      } else {
        int partial_index = -1;
        for (int i = 0; i < static_cast<int>(candidates.size()); ++i) {
          if (candidates[i] == "亜") partial_index = i;
        }
        if (!api->select_candidate(session, partial_index) ||
            !api->process_key(session, 'a', 0)) {
          result = Fail("select partial Japanese candidate and continue typing", 23);
        } else {
          std::vector<std::string> remaining;
          if (!ReadMenu(api, session, &remaining) || !Has(remaining, "愛")) {
            std::fprintf(stderr, "after partial selection input=%s remaining candidates:",
                         api->get_input(session));
            for (const auto& candidate : remaining)
              std::fprintf(stderr, " [%s]", candidate.c_str());
            std::fprintf(stderr, "\n");
            result = Fail("remaining Japanese input should retain its translator and offer 愛", 24);
          }
        }
      }
    }
    if (session) api->destroy_session(session);
  }

  if (!result) {
    // Shift_L is the Japanese-prefix ASCII escape. The next key must pass through.
    RimeSessionId session = NewSession(api);
    if (!session || !api->simulate_key_sequence(session, "ja")) {
      result = Fail("prepare bare Japanese prefix for ASCII escape", 15);
    } else {
      api->process_key(session, 0xffe1, 0);
      api->process_key(session, 0xffe1, 1 << 30);
      int ascii = api->get_option(session, "ascii_mode");
      int handled = api->process_key(session, 'j', 0);
      if (!ascii || !InputIs(api, session, "") || handled) {
        result = Fail("left Shift should exit prefix into direct ASCII", 16);
      }
    }
    if (session) api->destroy_session(session);
  }

  if (!result) {
    // Shift_R is not intercepted; the project's existing commit_code binding stays intact.
    RimeSessionId session = NewSession(api);
    if (!session || !api->simulate_key_sequence(session, "ja")) {
      result = Fail("prepare bare Japanese prefix for original Shift_R", 17);
    } else {
      api->process_key(session, 0xffe2, 0);
      api->process_key(session, 0xffe2, 1 << 30);
      std::string commit;
      if (!ReadCommit(api, session, &commit) || commit != "ja" ||
          !api->get_option(session, "ascii_mode")) {
        result = Fail("right Shift should retain default commit_code behavior", 18);
      }
    }
    if (session) api->destroy_session(session);
  }

  if (!result) {
    // zh_only must suppress the mounted Japanese translator/processor.
    RimeSessionId session = NewSession(api, false);
    if (!session || !api->simulate_key_sequence(session, "jaa")) {
      result = Fail("type with Japanese mode disabled", 19);
    } else {
      std::vector<std::string> candidates;
      if (InputIs(api, session, "jaあ") ||
          (ReadMenu(api, session, &candidates) && Has(candidates, "あ"))) {
        result = Fail("zh_only should not convert or translate Japanese prefix input", 20);
      }
    }
    if (session) api->destroy_session(session);
  }

  api->finalize();
  dlclose(plugin);
  return result;
}
