#!/usr/bin/env python3
"""Watcher que executa o script de auto-commit e push para o GitHub a cada alteração no workspace.

Uso: execute este script no mesmo ambiente virtual onde o projeto roda.
Ele observa mudanças de arquivos (excluindo .git, .venv, caches e arquivos sensíveis)
e, com debounce, aciona `scripts/auto_commit.py` para commitar e enviar ao GitHub.
"""
import argparse
import os
import sys
import time
import threading
from pathlib import Path
from subprocess import run

ROOT = Path(__file__).resolve().parent.parent

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except Exception:
    print("watchdog não encontrado. Instale com: pip install watchdog")
    sys.exit(1)


# Padrões de arquivos e pastas a ignorar para evitar loops ou versionar arquivos indevidos
IGNORAR_SUBSTRINGS = (
    os.sep + ".git" + os.sep,
    os.sep + ".venv" + os.sep,
    os.sep + "venv" + os.sep,
    os.sep + "__pycache__" + os.sep,
    os.sep + ".vscode" + os.sep,
    os.sep + ".idea" + os.sep,
    os.sep + "Certificados" + os.sep,
)

IGNORAR_EXTENSOES = (
    ".pyc", ".pyo", ".pyd", ".tmp", ".swp", ".pfx", ".p12"
)


class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, callback, debounce_seconds=2.0):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.timer = None
        self.lock = threading.Lock()

    def _deve_ignorar(self, path: str) -> bool:
        norm = os.path.normpath(path)
        base = os.path.basename(norm)

        # Arquivos temporários comuns
        if base.startswith("~$") or base.startswith(".~"):
            return True

        # Extensões ignoradas
        if any(base.endswith(ext) for ext in IGNORAR_EXTENSOES):
            return True

        # Pastas ignoradas
        norm_com_seps = f"{os.sep}{norm}{os.sep}"
        if any(sub in norm_com_seps for sub in IGNORAR_SUBSTRINGS):
            return True

        return False

    def on_any_event(self, event):
        if event.is_directory:
            return

        path = os.path.abspath(event.src_path)
        if self._deve_ignorar(path):
            return

        dest = getattr(event, "dest_path", None)
        if dest and self._deve_ignorar(os.path.abspath(dest)):
            return

        with self.lock:
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.debounce_seconds, self.callback)
            self.timer.daemon = True
            self.timer.start()


def run_auto_commit():
    """Roda o script de auto commit e push se houver algo para commitar."""
    py = sys.executable
    script = str(ROOT / "scripts" / "auto_commit.py")

    try:
        print("\n[auto-commit] Alteração detectada — executando commit e push para o GitHub...")
        result = run([py, script, "--push"], capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
    except Exception as e:
        print(f"Falha ao executar auto_commit: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitora alterações no workspace para auto-commit e push ao GitHub."
    )
    parser.add_argument(
        "--debounce",
        type=float,
        default=2.0,
        help="Segundos de espera após a última alteração antes de commitar (padrão: 2.0)",
    )
    args = parser.parse_args()

    print("==================================================")
    print("  Auto Commit & Push Watcher Ativo                ")
    print(f"  Diretório monitorado: {ROOT}")
    print(f"  Intervalo de debounce: {args.debounce}s")
    print("  Pressione Ctrl+C para encerrar.                 ")
    print("==================================================")

    event_handler = DebouncedHandler(
        run_auto_commit, debounce_seconds=args.debounce
    )
    observer = Observer()
    observer.schedule(event_handler, str(ROOT), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando watcher...")
        observer.stop()
    observer.join()
    print("Watcher finalizado.")


if __name__ == "__main__":
    main()
