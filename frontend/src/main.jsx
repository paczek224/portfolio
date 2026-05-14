import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import fallback from "./portfolio-fallback.json";
import "./styles.css";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8080";
const themes = [
  { id: "neon", label: "Neon" },
  { id: "matrix", label: "Matrix" },
  { id: "amber", label: "Amber" },
  { id: "paper", label: "Paper" },
];

function App() {
  const [profile, setProfile] = useState(fallback);
  const [theme, setTheme] = useState(() => localStorage.getItem("portfolio-theme") || "neon");

  useEffect(() => {
    fetch(`${apiUrl}/api/portfolio`)
      .then((response) => (response.ok ? response.json() : fallback))
      .then(setProfile)
      .catch(() => setProfile(fallback));
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("portfolio-theme", theme);
  }, [theme]);

  const services = useMemo(() => normalizeServices(profile), [profile]);
  const approach = normalizeApproach(profile.approach?.length ? profile.approach : fallback.approach);
  const links = normalizeLinks(profile.contact);
  const terminalLines = buildTerminalLines(profile);
  const skillGroups = normalizeSkillGroups(profile.skills);

  return (
    <main className="site-shell">
      <div className="grid-overlay" />
      <ThemeSwitcher activeTheme={theme} onThemeChange={setTheme} />

      <section className="hero">
        <div className="badge">{profile.badge || "portfolio · automation · backend quality"}</div>
        <h1>{profile.name}</h1>
        <p className="subtitle">{profile.tagline || profile.title || "Portfolio"}</p>
        <p className="summary">{profile.summary}</p>
        <div className="actions">
          {links.map((link) => (
            <a key={link.label} className={`button ${link.kind}`} href={link.href}>
              {link.label}
            </a>
          ))}
          {profile.resume?.url && (
            <a className="button outline" href={profile.resume.url} download>
              {profile.resume.label || "Download CV"}
            </a>
          )}
        </div>
        <div className="scroll-indicator">
          <span>scroll</span>
          <i />
        </div>
      </section>

      {profile.metrics?.length > 0 && (
        <section className="metrics-strip" aria-label="Impact metrics">
          {profile.metrics.map((metric) => (
            <article className="metric-card" key={`${metric.value}-${metric.label}`}>
              <strong>{metric.value}</strong>
              <span>{metric.label}</span>
            </article>
          ))}
        </section>
      )}

      <section className="panel terminal-panel" aria-label="Portfolio terminal">
        <div className="terminal">
          <div className="terminal-bar">
            <span>lukasz@quality:~$</span>
          </div>
          <div className="terminal-body">
            {terminalLines.map((line, index) => (
              <div className="terminal-line" key={`${line.text}-${index}`}>
                <span className={line.type}>{line.prefix}</span>
                <span>{line.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Section label="// what I do" title="Services">
        <div className="card-grid">
          {services.map((service) => (
            <article className="service-card" key={service.title}>
              <span className="service-icon">*</span>
              <h3>{service.title}</h3>
              <p>{service.description}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section label="// core stack" title="Skills">
        <div className="skill-grid">
          {skillGroups.map((group) => (
            <article className="skill-group" key={group.title}>
              <h3>{group.title}</h3>
              <div className="chip-list">
                {group.items.map((skill) => (
                  <span className="chip" key={skill}>{skill}</span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </Section>

      <Section label="// work history" title="Experience">
        <div className="timeline">
          {normalizeExperience(profile.experience).map((job) => (
            <article className="timeline-item" key={`${job.role}-${job.period}`}>
              <div className="timeline-meta">
                <span>{job.period}</span>
                {job.location && <span>{job.location}</span>}
              </div>
              <div className="timeline-content">
                <h3>{job.role}</h3>
                <p className="company">{[job.company, job.client].filter(Boolean).join(" · ")}</p>
                <ul>
                  {job.bullets.map((bullet) => (
                    <li key={bullet}>{bullet}</li>
                  ))}
                </ul>
                {job.stack.length > 0 && (
                  <div className="chip-list compact">
                    {job.stack.map((item) => (
                      <span className="chip" key={item}>{item}</span>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      </Section>

      <Section label="// how I work" title="Approach">
        <div className="approach-grid">
          {approach.map((item, index) => (
            <article className="approach-card" key={`${item.title}-${index}`}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </Section>

      {profile.caseStudies?.length > 0 && (
        <Section label="// proof of work" title="Case Studies">
          <div className="case-grid">
            {profile.caseStudies.map((study) => (
              <article className="case-card" key={study.title}>
                <h3>{study.title}</h3>
                <CaseLine label="Problem" value={study.problem} />
                <CaseLine label="Role" value={study.role} />
                <CaseLine label="Result" value={study.result} />
                {study.stack?.length > 0 && (
                  <div className="chip-list compact">
                    {study.stack.map((item) => (
                      <span className="chip" key={item}>{item}</span>
                    ))}
                  </div>
                )}
              </article>
            ))}
          </div>
        </Section>
      )}

      {profile.recommendations?.length > 0 && (
        <Section label="// recommendations" title="LinkedIn Recommendations">
          <div className="recommendation-grid">
            {profile.recommendations.map((recommendation) => (
              <article className="recommendation-card" key={recommendation.author}>
                <p>"{recommendation.quote}"</p>
                <div className="recommendation-author">
                  <strong>{recommendation.author}</strong>
                  <a href={recommendation.link}>{recommendation.source || "LinkedIn"}</a>
                </div>
              </article>
            ))}
          </div>
        </Section>
      )}

      <Section label="// selected work" title="Projects">
        {profile.projects?.length ? (
          <div className="project-list">
            {normalizeProjects(profile.projects).map((project, index) => (
              <article className="project-row" key={`${project.title}-${index}`}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <h3>{project.title}</h3>
                  <p>{project.description}</p>
                  {project.stack?.length > 0 && (
                    <div className="chip-list compact">
                      {project.stack.map((item) => (
                        <span className="chip" key={item}>{item}</span>
                      ))}
                    </div>
                  )}
                  {project.link && <a href={project.link}>Open project</a>}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">Sekcja uzupelni sie po dodaniu projektow.</p>
        )}
      </Section>

      <Section label="// background" title="Education & Certificates">
        <div className="info-grid">
          <InfoList title="Education" items={profile.education} primaryKey="school" secondaryKey="field" metaKey="period" />
          <InfoList title="Certifications" items={profile.certifications} primaryKey="name" secondaryKey="issuer" metaKey="date" />
          <InfoList title="Languages" items={profile.languages} primaryKey="name" secondaryKey="level" />
        </div>
      </Section>

      {profile.cooperation && (
        <section className="panel cooperation-panel">
          <p className="section-label">// availability</p>
          <h2>Cooperation Model</h2>
          <p className="cooperation-headline">{profile.cooperation.headline}</p>
          <div className="cooperation-grid">
            {(profile.cooperation.models || []).map((model) => (
              <span key={model}>{model}</span>
            ))}
          </div>
          <p className="cooperation-cta">{profile.cooperation.cta}</p>
        </section>
      )}

      <section className="contact-section" id="contact">
        <p className="section-label">// get in touch</p>
        <h2>Let's work together</h2>
        <p>{profile.cooperation?.cta || contactText(profile.contact)}</p>
        {profile.contact?.email && (
          <a className="contact-button" href={`mailto:${profile.contact.email}`}>
            {profile.contact.email}
          </a>
        )}
      </section>
    </main>
  );
}

function CaseLine({ label, value }) {
  if (!value) return null;
  return (
    <div className="case-line">
      <span>{label}</span>
      <p>{value}</p>
    </div>
  );
}

function ThemeSwitcher({ activeTheme, onThemeChange }) {
  return (
    <div className="theme-switcher" aria-label="Theme switcher">
      {themes.map((item) => (
        <button
          aria-label={`Use ${item.label} theme`}
          className={`theme-dot theme-${item.id}${activeTheme === item.id ? " active" : ""}`}
          key={item.id}
          onClick={() => onThemeChange(item.id)}
          title={item.label}
          type="button"
        />
      ))}
    </div>
  );
}

function Section({ label, title, children }) {
  return (
    <section className="panel">
      <p className="section-label">{label}</p>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function InfoList({ title, items = [], primaryKey, secondaryKey, metaKey }) {
  return (
    <article className="info-card">
      <h3>{title}</h3>
      {items.map((item) => (
        <div className="info-row" key={`${item[primaryKey]}-${item[metaKey] || item[secondaryKey]}`}>
          <strong>{item[primaryKey]}</strong>
          {item[secondaryKey] && <span>{item[secondaryKey]}</span>}
          {metaKey && item[metaKey] && <small>{item[metaKey]}</small>}
        </div>
      ))}
    </article>
  );
}

function normalizeServices(profile) {
  const services = profile.services?.length ? profile.services : fallback.services;
  return services.slice(0, 6).map((service) => {
    if (typeof service === "object") {
      return {
        title: service.title || "Technical delivery",
        description: service.description || "Projektowanie i dowozenie praktycznych rozwiazan.",
      };
    }
    return { title: service, description: service };
  });
}

function normalizeApproach(items = []) {
  return items.map((item) => {
    if (typeof item === "object") {
      return {
        title: item.title || "Pragmatic delivery",
        description: item.description || "",
      };
    }
    return {
      title: item.split(" ").slice(0, 3).join(" ").replace(/[.,;:]$/, ""),
      description: item,
    };
  });
}

function normalizeSkillGroups(skills) {
  if (!skills) return [];
  if (Array.isArray(skills)) {
    return [{ title: "Core", items: skills }];
  }
  return Object.entries(skills).map(([key, items]) => ({
    title: titleFromKey(key),
    items: Array.isArray(items) ? items : [],
  }));
}

function normalizeExperience(experience = []) {
  return experience.map((item) => {
    if (typeof item === "object") {
      return {
        role: item.role || "Experience",
        company: item.company || "",
        client: item.client || "",
        location: item.location || "",
        period: item.period || "",
        bullets: item.bullets || [],
        stack: item.stack || [],
      };
    }
    return {
      role: item,
      company: "",
      client: "",
      location: "",
      period: "",
      bullets: [],
      stack: [],
    };
  });
}

function normalizeProjects(projects = []) {
  return projects.map((project) => {
    if (typeof project === "object") {
      return project;
    }
    return { title: project, description: "", link: "" };
  });
}

function buildTerminalLines(profile) {
  const highlights = profile.highlights?.length ? profile.highlights.slice(0, 4) : [];
  const lines = [
    { prefix: "$", text: "run qa-profile --from Lukasz_Paczek_cv.pdf", type: "prompt" },
    { prefix: "✓", text: `${profile.title || "Portfolio profile"} loaded`, type: "pass" },
  ];
  highlights.forEach((item) => lines.push({ prefix: ">", text: item, type: "dim" }));
  lines.push({ prefix: "✓", text: `contact: ${profile.contact?.email || "available on request"}`, type: "pass" });
  return lines;
}

function normalizeLinks(contact = {}) {
  const links = [];
  if (contact.linkedin) links.push({ label: "LinkedIn", href: ensureUrl(contact.linkedin), kind: "primary" });
  if (contact.github) links.push({ label: "GitHub", href: ensureUrl(contact.github), kind: "outline" });
  if (contact.email) links.push({ label: "Email", href: `mailto:${contact.email}`, kind: "success" });
  return links.length ? links : [{ label: "Contact", href: "#contact", kind: "primary" }];
}

function ensureUrl(value) {
  return /^https?:\/\//i.test(value) ? value : `https://${value}`;
}

function titleFromKey(key) {
  return key
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (letter) => letter.toUpperCase());
}

function contactText(contact = {}) {
  const parts = [];
  if (contact.location) parts.push(contact.location);
  if (contact.phone) parts.push(contact.phone);
  return parts.length ? parts.join(" · ") : "Remote collaboration · project-based work · fast iteration";
}

createRoot(document.getElementById("root")).render(<App />);
