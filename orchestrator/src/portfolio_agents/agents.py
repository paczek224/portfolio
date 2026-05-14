from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .llm_client import LlmClient
from .models import PortfolioProfile
from .workspace import write_json


SYSTEM_PROMPT = """Jestes agentem pomagajacym stworzyc proste portfolio.
Zwracaj tylko poprawny JSON, bez markdowna i bez komentarzy."""


@dataclass
class AgentResult:
    agent: str
    message: str
    files: list[str]


class OrchestratorAgent:
    def __init__(self, llm: LlmClient, project_root: Path):
        self.llm = llm
        self.project_root = project_root

    def run(self, cv_text: str) -> list[AgentResult]:
        profile = self._extract_profile(cv_text)
        generated_path = self.project_root / "generated" / "portfolio.json"
        write_json(generated_path, profile.to_dict())

        backend = BackendAgent(self.project_root)
        frontend = FrontendAgent(self.project_root)

        return [
            AgentResult("orchestrator", "CV przetworzone do wspolnego modelu danych.", [str(generated_path)]),
            backend.prepare(profile),
            frontend.prepare(profile),
        ]

    def _extract_profile(self, cv_text: str) -> PortfolioProfile:
        response = self.llm.complete(
            SYSTEM_PROMPT,
            "Wyodrebnij z CV dane portfolio jako JSON z polami: "
            "name, title, summary, skills, experience, projects, services, approach, contact. "
            "Pole services ma zawierac 3-6 krotkich ofert/uslug wynikajacych z CV. "
            "Pole approach ma zawierac 3-4 zasady pracy.\n\nCV:\n"
            + cv_text[:12000],
        )

        if not response.used_fallback:
            parsed = _parse_json_object(response.text)
            if parsed:
                return PortfolioProfile(
                    name=str(parsed.get("name") or "Twoje Imie i Nazwisko"),
                    title=str(parsed.get("title") or "Portfolio"),
                    summary=str(parsed.get("summary") or ""),
                    skills=_as_string_list(parsed.get("skills")),
                    experience=_as_string_list(parsed.get("experience")),
                    projects=_as_string_list(parsed.get("projects")),
                    services=_as_string_list(parsed.get("services")),
                    approach=_as_string_list(parsed.get("approach")),
                    contact=_as_string_map(parsed.get("contact")),
                )

        return _fallback_profile(cv_text)


class BackendAgent:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def prepare(self, profile: PortfolioProfile) -> AgentResult:
        path = self.project_root / "backend" / "src" / "main" / "resources" / "portfolio.json"
        write_json(path, profile.to_dict())
        return AgentResult("backend", "Dane portfolio zapisane dla API Spring Boot.", [str(path)])


class FrontendAgent:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def prepare(self, profile: PortfolioProfile) -> AgentResult:
        path = self.project_root / "frontend" / "src" / "portfolio-fallback.json"
        write_json(path, profile.to_dict())
        return AgentResult("frontend", "Fallback danych zapisany dla Reacta.", [str(path)])


def _parse_json_object(text: str) -> dict | None:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?", "", candidate).strip()
        candidate = re.sub(r"```$", "", candidate).strip()

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        return None

    try:
        data = json.loads(candidate[start : end + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _as_string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _as_string_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(val) for key, val in value.items() if str(val).strip()}


def _fallback_profile(cv_text: str) -> PortfolioProfile:
    lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
    name = _guess_name(lines)
    email = next((item for item in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", cv_text)), "")
    phone = next((item for item in re.findall(r"(?:\+?\d[\d\s-]{7,}\d)", cv_text)), "")
    skills = _guess_skills(cv_text)
    experience = _section_lines(cv_text, "doswiadczenie")
    projects = _section_lines(cv_text, "projekty")

    return PortfolioProfile(
        name=name,
        title="Portfolio",
        summary="Profil wygenerowany heurystycznie. Uruchom lokalny model, aby uzyskac lepszy opis.",
        skills=skills,
        experience=experience or _non_contact_lines(lines[1:5]),
        projects=projects,
        services=_fallback_services(skills),
        approach=[
            "Szybkie zrozumienie celu i zakresu projektu.",
            "Jasna komunikacja oraz male, regularne iteracje.",
            "Rozwiazania budowane tak, aby dalo sie je utrzymywac.",
        ],
        contact={key: value for key, value in {"email": email, "phone": phone}.items() if value},
    )


def _guess_skills(cv_text: str) -> list[str]:
    known = [
        "Python",
        "Java",
        "Spring Boot",
        "React",
        "Angular",
        "SQL",
        "Docker",
        "Git",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
    ]
    lowered = cv_text.lower()
    return [skill for skill in known if skill.lower() in lowered]


def _section_lines(cv_text: str, heading: str) -> list[str]:
    lines = [line.strip() for line in cv_text.splitlines()]
    result: list[str] = []
    inside = False
    for line in lines:
        normalized = line.lower().strip(" :")
        if normalized == heading:
            inside = True
            continue
        if inside and normalized in {"doswiadczenie", "projekty", "umiejetnosci", "skills"}:
            break
        if inside and line:
            result.append(line)
    return result[:6]


def _non_contact_lines(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        if "@" in line or re.search(r"\+?\d[\d\s-]{7,}\d", line):
            continue
        cleaned.append(line)
    return cleaned


def _guess_name(lines: list[str]) -> str:
    for line in lines[:12]:
        normalized = line.lower()
        if line.startswith("---") or "page" in normalized or "personal info" in normalized:
            continue
        if "@" in line or re.search(r"\+?\d[\d\s-]{7,}\d", line):
            continue
        if len(line.split()) >= 2:
            return line
    return lines[0] if lines else "Twoje Imie i Nazwisko"


def _fallback_services(skills: list[str]) -> list[str]:
    services = []
    if any(skill in skills for skill in ["Java", "Spring Boot"]):
        services.append("Backend API w Java i Spring Boot")
    if any(skill in skills for skill in ["React", "Angular", "JavaScript", "TypeScript"]):
        services.append("Responsywne aplikacje frontendowe")
    if "Python" in skills:
        services.append("Automatyzacja i narzedzia w Pythonie")
    if "SQL" in skills:
        services.append("Integracje danych i praca z bazami SQL")
    if "Docker" in skills:
        services.append("Konteneryzacja i przygotowanie srodowisk")
    return services or ["Aplikacje webowe", "Automatyzacja procesow", "Wsparcie techniczne projektu"]
