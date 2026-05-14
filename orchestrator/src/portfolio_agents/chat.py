from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

from .agents import OrchestratorAgent
from .config import Settings
from .llm_client import LlmClient
from .workspace import read_cv


HELP_TEXT = """
Dostepne polecenia:
- generuj portfolio z ../input/cv.pdf
- przetworz ../input/cv.txt
- pokaz dane
- model
- pomoc
- wyjdz
""".strip()


class ChatSession:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = LlmClient(settings)
        self.orchestrator = OrchestratorAgent(self.llm, settings.project_root)

    def run(self) -> None:
        print("Portfolio multi-agent chat")
        print("Wpisz 'pomoc', zeby zobaczyc komendy. Wpisz 'wyjdz', zeby zakonczyc.")

        while True:
            try:
                command = input("\nagent> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nKoniec pracy.")
                return

            if not command:
                continue

            should_continue = self.handle(command)
            if not should_continue:
                return

    def handle(self, command: str) -> bool:
        normalized = command.lower().strip()

        if normalized in {"wyjdz", "exit", "quit", "q"}:
            print("Koniec pracy.")
            return False

        if normalized in {"pomoc", "help", "?"}:
            print(HELP_TEXT)
            return True

        if normalized in {"model", "jaki model", "pokaz model"}:
            self._print_model()
            return True

        if normalized in {"pokaz dane", "dane", "portfolio"}:
            self._print_generated_data()
            return True

        cv_path = _extract_cv_path(command)
        if cv_path:
            self._generate_from_cv(cv_path)
            return True

        self._unknown_command(command)
        return True

    def _generate_from_cv(self, cv_path: Path) -> None:
        resolved = _resolve_path(self.settings.project_root, cv_path)
        if not resolved.exists():
            print(f"Nie widze pliku: {resolved}")
            return

        try:
            cv_text = read_cv(resolved)
        except Exception as exc:
            print(f"Nie udalo sie odczytac CV: {exc}")
            return

        print("Uruchamiam agentow: orkiestrator -> backend -> frontend...")
        results = self.orchestrator.run(cv_text)
        print("Gotowe:")
        for result in results:
            print(f"- {result.agent}: {result.message}")
            for file_path in result.files:
                print(f"  -> {file_path}")

    def _print_generated_data(self) -> None:
        path = self.settings.project_root / "generated" / "portfolio.json"
        if not path.exists():
            print("Nie ma jeszcze generated/portfolio.json. Najpierw wygeneruj portfolio z CV.")
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps(data, ensure_ascii=False, indent=2))

    def _print_model(self) -> None:
        print(f"Provider: {self.settings.llm_provider}")
        print(f"Base URL: {self.settings.llm_base_url}")
        print(f"Model: {self.settings.llm_model}")

    def _unknown_command(self, command: str) -> None:
        print(f"Nie rozumiem jeszcze polecenia: {command}")
        print("Na start obsluguje proste komendy. Wpisz 'pomoc'.")


def _extract_cv_path(command: str) -> Path | None:
    lowered = command.lower()
    if not any(word in lowered for word in ["generuj", "wygeneruj", "przetworz", "przetwórz"]):
        return None

    tokens = shlex.split(command, posix=False)
    for token in reversed(tokens):
        cleaned = token.strip().strip('"').strip("'")
        if re.search(r"\.(pdf|txt|md)$", cleaned, re.IGNORECASE):
            return Path(cleaned)
    return None


def _resolve_path(project_root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    return (project_root / path).resolve()
