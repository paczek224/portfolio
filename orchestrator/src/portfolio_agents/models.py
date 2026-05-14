from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PortfolioProfile:
    name: str = "Twoje Imie i Nazwisko"
    title: str = "Portfolio"
    summary: str = "Krotki opis zawodowy pojawi sie tutaj po przetworzeniu CV."
    skills: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    approach: list[str] = field(default_factory=list)
    contact: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "summary": self.summary,
            "skills": self.skills,
            "experience": self.experience,
            "projects": self.projects,
            "services": self.services,
            "approach": self.approach,
            "contact": self.contact,
        }
