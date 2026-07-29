#!/usr/bin/env python3
"""Watcher simples que executa o script de auto-commit quando há alterações no workspace.

Uso: execute este script no mesmo ambiente virtual onde o projeto roda.
Ele observa mudanças de arquivo (exclui .git) e, com debounce, roda o script
`scripts/auto_commit.py` para criar um commit automático.
"""
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


class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, callback, debounce_seconds=1.0, ignore_paths=None):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.timer = None
        self.lock = threading.Lock()
        self.ignore_paths = set(ignore_paths or [])

    def on_any_event(self, event):
        path = os.path.abspath(event.src_path)
        # Ignorar .git e arquivos temporários
        if any(p in path for p in ("/.git/", "\\.git\\")):
            return
        if any(path.endswith(ip) or ip in path for ip in self.ignore_paths):
            return

        with self.lock:
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.debounce_seconds, self.callback)
            self.timer.daemon = True
            self.timer.start()


def run_auto_commit():
    """Roda o script de auto commit se houver algo para commitar."""
    # Usar o mesmo interpretador que executa este watcher
    py = sys.executable
    script = str(ROOT / "scripts" / "auto_commit.py")

    # Verificar se há mudanças a commitar
    try:
        check_status = run([py, script, "--no-add"], capture_output=True, text=True)
        # O script com --no-add apenas imprime quando não há alterações
    except Exception as e:
        print(f"Erro ao executar auto_commit: {e}")
        return

    # Sempre executar o auto_commit para que ele faça add+commit quando houver
    try:
        print("[auto-commit] Detectada alteração — criando commit automático e enviando para remoto...")
        run([py, script, "--push"], check=True)
    except Exception as e:
        print(f"Falha ao executar auto_commit: {e}")


def main():
    print("Iniciando Auto Commit Watcher...")
    ignore = [str(ROOT / ".venv"), str(ROOT / "venv"), str(ROOT / "node_modules")]

    event_handler = DebouncedHandler(run_auto_commit, debounce_seconds=1.5, ignore_paths=ignore)
    observer = Observer()
    observer.schedule(event_handler, str(ROOT), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
