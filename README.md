# Telix-Shipshield

Telix Shipshield is a universal project execution, verification, and delivery platform that transforms ideas into actionable, trackable projects. It helps individuals and teams plan roadmaps, manage tasks and resources, monitor progress, identify risks, preserve project knowledge, and verify outcomes with evidence.

# Telix ShipShield

**Plan clearly. Execute confidently. Verify progress. Deliver with proof.**

Telix ShipShield is a project planning, execution, and delivery-readiness platform designed to help people turn ideas into structured, verifiable outcomes.

Whether you're building software, launching a business, organizing an event, managing a research initiative, or coordinating another kind of project, ShipShield aims to provide a clear view of what needs to happen, what has been completed, what remains blocked, and what evidence supports the final result.

> From ideas to verified delivery—for software, teams, and every kind of project.

---

## The Problem

Projects often become difficult to manage when requirements are unclear, tasks lack measurable outcomes, progress updates cannot be verified, and important delivery requirements are overlooked.

Software repositories introduce additional challenges: documentation becomes outdated, tests may be missing, dependencies can go unreviewed, and teams can struggle to communicate whether a project is genuinely ready for release.

Telix ShipShield is being developed to address these problems through structured planning, evidence-backed execution, and transparent readiness assessments.

## Our Approach

Telix ShipShield is designed around five principles:

- **Plan:** Transform project ideas and requirements into editable plans, milestones, tasks, and acceptance criteria.
- **Execute:** Track task progress, dependencies, blockers, and outstanding work.
- **Verify:** Associate completed work with evidence instead of relying exclusively on status labels.
- **Assess:** Identify risks, missing requirements, and unresolved blockers before delivery.
- **Deliver:** Produce a clear readiness summary and help keep project documentation aligned with the work performed.

AI-generated recommendations should remain editable and subject to human review. A suggested plan is not an approved plan, and a marked-complete task is not automatically verified.

## Key Capabilities

The following capabilities describe the product direction; individual features are implemented incrementally.

### Universal Project Management

- Create and organize projects of different types.
- Define project objectives, scope, milestones, and deliverables.
- Generate and edit structured project plans.
- Manage tasks, dependencies, deadlines, and blockers.
- Define acceptance criteria for measurable completion.
- Track project health and outstanding risks.

### Evidence-Based Progress

- Attach evidence to tasks and deliverables.
- Distinguish reported progress from verified completion.
- Identify missing evidence and unmet acceptance criteria.
- Generate delivery-readiness assessments.
- Explain why a project is ready, at risk, blocked, or still unverified.

### AI Project Assistant

- Turn project descriptions into structured plans.
- Recommend milestones, tasks, and acceptance criteria.
- Identify gaps, dependencies, and potential risks.
- Help users understand project status and next steps.
- Keep AI-generated outputs editable and subject to approval.

### Software Repository Intelligence

For projects with connected source repositories, ShipShield aims to provide optional software-specific checks, including:

- Repository structure and documentation reviews.
- README accuracy and completeness checks.
- Inspection of dependency manifests and available test configuration.
- Identification of missing project documentation and potential delivery risks.
- Repository-readiness reports with supporting file references.
- Proposed README updates presented as a diff for review before changes are applied.

Repository analysis should distinguish observed facts from assumptions. A configured test suite does not prove that tests pass, and a repository review does not replace a complete security audit.

### Delivery Documentation

- Summarize completed and outstanding work.
- Highlight unresolved blockers and delivery risks.
- Maintain a clear record of evidence and decisions.
- Help keep project documentation aligned with verified changes.

---

## Current Development Status

**Status:** Early development / hackathon MVP.

ShipShield is being built incrementally. The repository structure and development environment are being prepared before the core project workflows are implemented.

| Area                   | Current direction                                             |
| ---------------------- | ------------------------------------------------------------- |
| Backend                | Django modular monolith                                       |
| Database               | PostgreSQL                                                    |
| Project management     | Projects, milestones, tasks, and criteria                     |
| Evidence               | Evidence-backed completion and readiness assessments          |
| AI                     | Alan AI integration, subject to API and platform validation   |
| Repository integration | Optional GitHub inspection and reviewed documentation updates |
| Interface              | Premium, dark, technical product experience                   |
| Deployment             | To be configured and verified                                 |

The status table describes the intended architecture and development direction, not a claim that each capability is already operational.

## Technology Stack

- **Language:** Python
- **Web framework:** Django
- **Database:** PostgreSQL
- **Database driver:** Psycopg
- **Configuration:** Environment variables with `python-dotenv`
- **Repository integration:** GitHub API tooling, planned for the integration layer
- **Testing:** Django testing tools, pytest, and pytest-django
- **Code quality:** Ruff
- **Deployment preparation:** Gunicorn and WhiteNoise

The stack may evolve as implementation and integration requirements become clearer.

## Architecture

ShipShield uses a modular Django application structure so project planning, evidence management, AI assistance, and external integrations can evolve independently within one application.

```text
Telix-Shipshield/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── projects/
│   ├── planning/
│   ├── evidence/
│   ├── assistant/
│   └── integrations/
├── templates/
├── static/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The exact structure may expand as the application develops.

## Getting Started

### Prerequisites

Install the following before running the application:

- Python 3.13 or another supported Python version.
- PostgreSQL.
- Git.
- PowerShell on Windows, or an equivalent terminal.

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Telix-Shipshield
```

If you're already working in the local project directory, skip this step.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file based on `.env.example`.

```powershell
Copy-Item .env.example .env
```

Configure the following values in `.env`:

```dotenv
SECRET_KEY=your-generated-django-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=telix_shipshield
DB_USER=shipshield_app
DB_PASSWORD=your-local-database-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Replace the example values with your actual local configuration. Generate a strong Django secret key and use a strong PostgreSQL password.

**Never commit `.env` or expose database credentials and secret keys in source code, screenshots, issue reports, or public repositories.** Use `.env.example` to document required variables without including real secrets.

### 5. Create the PostgreSQL database

Once PostgreSQL is installed and running, create a dedicated application role and database using PostgreSQL's administrative tools.

For example, from a PostgreSQL administrative session:

```sql
CREATE USER shipshield_app WITH PASSWORD 'replace_with_a_strong_password';
CREATE DATABASE telix_shipshield OWNER shipshield_app;
```

Use the same database name, username, and password in `.env`. Execute these commands only if the role and database do not already exist. For an existing setup, inspect it first rather than creating duplicate resources.

### 6. Run database migrations

```powershell
python manage.py migrate
```

### 7. Start the development server

```powershell
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

The development server starts Django; the final product interface and application workflows will become available as they are implemented.

---

## Development Principles

ShipShield is being developed with the following principles in mind:

1. **Evidence over assumptions:** distinguish claimed progress from verified results.
2. **Human approval:** require review before approving generated plans or applying consequential changes.
3. **Transparency:** explain readiness findings and identify the evidence supporting them.
4. **Security by design:** keep credentials server-side, protect connected repositories, and minimize unnecessary permissions.
5. **Universal applicability:** support general projects, with software-specific functionality enabled when relevant.
6. **Incremental delivery:** prioritize working, tested workflows over superficial feature counts.
7. **Honest reporting:** never represent an unrun test, unverified integration, or unimplemented feature as complete.

## Roadmap

The development roadmap prioritizes a usable foundation before more advanced integrations.

- [ ] Establish the Django and PostgreSQL foundation.
- [ ] Implement project creation and project overview pages.
- [ ] Add milestones, tasks, dependencies, and acceptance criteria.
- [ ] Support task status updates and project progress tracking.
- [ ] Implement evidence attachments and verification states.
- [ ] Generate transparent delivery-readiness reports.
- [ ] Integrate Alan AI for structured planning and project assistance.
- [ ] Add optional GitHub repository analysis.
- [ ] Propose README updates with reviewable diffs and explicit approval.
- [ ] Add automated tests, security checks, and deployment configuration.
- [ ] Prepare a working demonstration covering software and non-software projects.

Roadmap items should be checked off only when the relevant functionality has been implemented and verified.

## Project Vision

Telix ShipShield aims to make project delivery more predictable and trustworthy by connecting plans, execution, evidence, and readiness in one place.

The goal is not merely to show that work has been marked complete. It is to help people understand what has actually been delivered, what supports that conclusion, and what still needs attention.

**Telix ShipShield — Build with direction. Deliver with confidence.**

---

## License

The project's license has not yet been specified. Licensing terms will be added once the intended distribution and reuse policy has been decided.
