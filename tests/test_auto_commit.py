from auto_commit import build_commit_message
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class AutoCommitTests(unittest.TestCase):
    def test_custom_message_is_preserved(self) -> None:
        self.assertEqual(build_commit_message(
            "feat: adicionar automação"), "feat: adicionar automação")

    def test_docs_message_for_markdown_files(self) -> None:
        self.assertEqual(build_commit_message(
            None, ["M README.md"]), "docs: atualizar documentação")

    def test_python_message_for_python_changes(self) -> None:
        self.assertEqual(
            build_commit_message(
                None, ["M app.py", "M scripts/auto_commit.py"]),
            "chore: atualizar código Python",
        )


if __name__ == "__main__":
    unittest.main()
