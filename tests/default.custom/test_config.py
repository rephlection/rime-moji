#!/usr/bin/env python3
"""Smoke tests for default.custom component includes and patch fragments."""

from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CUSTOM = ROOT / "default.custom.yaml"
COMPONENTS = ("ascii_composer", "key_binder", "punctuator", "recognizer", "selector")


def load_yaml(path):
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def resolve_include(include):
    config_id, node_path = include.split(":", 1)
    config_path = ROOT / f"{config_id}.yaml"
    value = load_yaml(config_path)
    for key in node_path.strip("/").split("/"):
        value = value[key]
    return value


class DefaultCustomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_yaml(DEFAULT_CUSTOM)
        cls.patch = cls.config["patch"]

    def test_all_processor_includes_resolve_inside_patch(self):
        for component in COMPONENTS:
            with self.subTest(component=component):
                include = self.patch[component]["__include"]
                self.assertEqual(resolve_include(include), load_yaml(
                    ROOT / "default.custom" / "processor" / f"{component}.yaml"
                )[component])

    def test_recognizer_include_contains_patterns_mapping(self):
        included = resolve_include(self.patch["recognizer"]["__include"])
        self.assertIn("patterns", included)
        self.assertIn("email", included["patterns"])

    def test_key_binder_append_contains_custom_bindings(self):
        included = resolve_include(self.patch["key_binder"]["__include"])
        binding_patch = included["bindings"]["__patch"]
        additions = resolve_include(binding_patch[0])["__append"]
        self.assertTrue(any(binding.get("accept") == "bracketleft" for binding in additions))
        self.assertTrue(any(binding.get("select") == ".next" for binding in additions))

    def test_selector_bindings_share_one_included_node(self):
        selector = load_yaml(ROOT / "default.custom" / "processor" / "selector.yaml")
        patch = selector["selector"]["__patch"]
        include_refs = [patch[key]["__include"] for key in (
            "bindings", "linear/bindings", "vertical/bindings", "vertical/linear/bindings"
        )]
        self.assertEqual(len(set(include_refs)), 1)
        self.assertEqual(resolve_include(include_refs[0]), selector["rotate_candidate_with_tab"])


if __name__ == "__main__":
    unittest.main()
