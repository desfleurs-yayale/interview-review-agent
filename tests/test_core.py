from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TranscribeHelpersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module("transcribe", "scripts/1_transcribe.py")

    def test_replacement_is_reported(self):
        self.assertEqual(
            self.module.apply_replacements("CRI demo"),
            ("CLI demo", [("CRI", "CLI")]),
        )

    def test_output_names_never_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sample_speakers.txt"
            self.assertEqual(self.module.non_overwriting_path(output), output)
            output.write_text("first", encoding="utf-8")
            self.assertEqual(
                self.module.non_overwriting_path(output).name,
                "sample_speakers-2.txt",
            )
            (Path(directory) / "sample_speakers-2.txt").write_text(
                "second", encoding="utf-8"
            )
            self.assertEqual(
                self.module.non_overwriting_path(output).name,
                "sample_speakers-3.txt",
            )


class PrivacyScannerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module("privacy_scan", "scripts/privacy_scan.py")

    def test_sensitive_patterns_are_detected(self):
        samples = {
            "/Users/" + "alice/Desktop/file": "macOS home path",
            "192" + ".168.1.25": "private IPv4 address",
            "10" + ".0.0.8": "private IPv4 address",
            "172" + ".16.0.2": "private IPv4 address",
            "oc_" + "1234567890abcdef": "Feishu chat id",
        }
        for sample, expected in samples.items():
            with self.subTest(sample=sample):
                labels = [
                    label
                    for label, pattern in self.module.PATTERNS.items()
                    if pattern.search(sample)
                ]
                self.assertIn(expected, labels)


class FeishuSenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module(
            "send_feishu_summary",
            "skills/interview-agent/scripts/send_feishu_summary.py",
        )

    def test_explicit_chat_id_wins(self):
        self.assertEqual(
            self.module.resolve_chat_id("cli", {}, "explicit-id", None),
            "explicit-id",
        )

    def test_exact_chat_name_is_resolved(self):
        original = self.module.run_cli
        self.module.run_cli = lambda *args, **kwargs: {
            "data": {"chats": [{"name": "target", "chat_id": "resolved-id"}]}
        }
        try:
            self.assertEqual(
                self.module.resolve_chat_id("cli", {}, None, "target"),
                "resolved-id",
            )
        finally:
            self.module.run_cli = original


if __name__ == "__main__":
    unittest.main()
