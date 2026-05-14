from __future__ import annotations

import argparse
from pathlib import Path

from .agents import OrchestratorAgent
from .chat import ChatSession
from .config import load_settings
from .llm_client import LlmClient
from .workspace import read_cv


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate portfolio starter data from a CV.")
    parser.add_argument("mode", nargs="?", choices=["chat"], help="Start interactive chat mode.")
    parser.add_argument("--cv", help="Path to CV file: .pdf, .txt or .md.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    settings = load_settings(project_root)

    if args.mode == "chat":
        ChatSession(settings).run()
        return

    if not args.cv:
        parser.error("--cv is required unless you use chat mode.")

    llm = LlmClient(settings)
    cv_text = read_cv(Path(args.cv).resolve())

    results = OrchestratorAgent(llm, project_root).run(cv_text)

    print("Multi-agent run complete:")
    for result in results:
        print(f"- {result.agent}: {result.message}")
        for file_path in result.files:
            print(f"  -> {file_path}")
