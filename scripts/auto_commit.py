#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent


def run_git(args: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise RuntimeError(f"git {' '.join(args)} failed: {message}")
    return completed


def get_status_lines() -> List[str]:
    completed = run_git(["status", "--porcelain"])
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def build_commit_message(
    provided_message: Optional[str] = None,
    status_lines: Optional[List[str]] = None,
) -> str:
    if provided_message and provided_message.strip():
        return provided_message.strip()

    if not status_lines:
        return "chore: sem alterações para commitar"

    changed_paths = [line[3:] if len(
        line) > 3 else line for line in status_lines]
    lower_paths = [path.lower() for path in changed_paths]

    if any(path.endswith((".md", ".rst", ".txt")) for path in lower_paths):
        return "docs: atualizar documentação"
    if any(path.endswith(".py") for path in lower_paths) or any(path.startswith("scripts/") for path in lower_paths):
        return "chore: atualizar código Python"
    if any(path.endswith(".json") for path in lower_paths):
        return "chore: atualizar dados"
    return "chore: atualizar projeto"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage and commit workspace changes.")
    parser.add_argument("--message", help="Mensagem específica para o commit")
    parser.add_argument("--push", action="store_true",
                        help="Enviar o commit para o remoto após criar")
    parser.add_argument("--no-add", action="store_true",
                        help="Não adicionar automaticamente as alterações")
    args = parser.parse_args()

    status_lines = get_status_lines()
    if not status_lines:
        print("Nenhuma alteração para commitar.")
        return 0

    if not args.no_add:
        run_git(["add", "-A"])

    message = build_commit_message(args.message, status_lines)
    print(f"Mensagem do commit: {message}")

    commit_result = run_git(["commit", "-m", message], check=False)
    if commit_result.returncode != 0:
        stderr = (commit_result.stderr or commit_result.stdout).strip()
        print(stderr or "Commit não foi criado.")
        return commit_result.returncode

    print("Commit criado com sucesso.")
    if args.push:
        push_result = run_git(["push"], check=False)
        if push_result.returncode != 0:
            print((push_result.stderr or push_result.stdout).strip()
                  or "Falha ao enviar para o remoto.")
            return push_result.returncode
        print("Alterações enviadas para o remoto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
