# 🛡️ Telix ShipShield
- Live MVP: [telix-shipshield.onrender.com](https://telix-shipshield.onrender.com)
### Plan clearly. Execute confidently. Verify progress. Deliver with proof.

**Telix ShipShield** is an early-stage project execution and delivery-assurance platform designed to help people turn ideas into structured plans, track progress, organize evidence, and understand what remains before a project is ready to deliver.

Projects rarely fail because people lack ideas. They often struggle with unclear requirements, disconnected tasks, invisible risks, missing evidence, outdated documentation, and uncertainty about whether the final result is actually ready.

ShipShield is being built to address that gap.

Starting with a functional Django MVP, the long-term vision is to develop an AI-assisted platform that connects project planning, execution, repository intelligence, verification, and delivery documentation in one transparent workflow.

> **The core principle:** A project should not be considered ready merely because someone says it is finished. Its progress, evidence, limitations, and verification status should be visible.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Try%20ShipShield-0f766e?style=for-the-badge)](https://telix-shipshield.onrender.com)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Source%20Code-181717?style=for-the-badge&logo=github)](https://github.com/SamuelNiiOdoiOddoye/Telix-Shipshield)
[![Python](https://img.shields.io/badge/Python-Django-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)

**Project:** Telix ShipShield  
**Developer:** Samuel Nii Odoi Oddoye  
**Stage:** Hackathon MVP / early-stage development  
**Product direction:** AI-assisted project execution, verification, and delivery assurance

---

## 📌 Table of Contents

- [The Problem](#-the-problem)
- [The Vision](#-the-vision)
- [What Works Today](#-what-works-today)
- [The Proposed Product Workflow](#-the-proposed-product-workflow)
- [What Makes ShipShield Different](#-what-makes-shipshield-different)
- [Current MVP vs. Full Product](#-current-mvp-vs-full-product)
- [AI Integration and Hackathon Context](#-ai-integration-and-hackathon-context)
- [Technology Stack](#-technology-stack)
- [Architecture and Engineering Principles](#-architecture-and-engineering-principles)
- [Getting Started](#-getting-started)
- [Testing and Verification](#-testing-and-verification)
- [Roadmap](#-roadmap)
- [Known Limitations](#-known-limitations)
- [Who ShipShield Is For](#-who-shipshield-is-for)
- [Contributing and Collaboration](#-contributing-and-collaboration)
- [License](#-license)

---

## 🎯 The Problem

Modern project work is spread across issue trackers, repositories, documents, spreadsheets, chat applications, task boards, and testing tools.

A task may be marked complete without supporting evidence. A repository may contain a README that no longer describes the application. A milestone may be considered finished even though its acceptance criteria have not been met. A project owner may have no reliable way to distinguish reported progress from independently verified results.

These problems affect more than software development. They can appear in research, business operations, product development, personal projects, and other work that involves planning and delivery.

ShipShield explores a central question:

**What if a project had a structured, evidence-aware path from its initial idea to a clearly assessed delivery state?**

The goal is not simply to create another task manager. It is to connect the plan, the work, the supporting evidence, and the final assessment.

## 💡 The Vision

Telix ShipShield aims to become a universal project execution and delivery-assurance platform.

The intended product will help users:

- Translate an idea, problem, or objective into a structured project blueprint.
- Define milestones, tasks, dependencies, risks, and acceptance criteria.
- Maintain context as a project evolves.
- Track progress against the original plan.
- Collect evidence supporting completed work.
- Connect relevant repositories, documentation, and development tools.
- Identify gaps between what a project claims and what its available evidence demonstrates.
- Assess delivery readiness using transparent criteria.
- Generate proposed documentation updates and delivery reports for human review.
- Preserve a useful record of decisions, progress, verification, and outstanding work.

Although software development is the initial focus, the underlying concepts are intended to support projects beyond coding.

For example, a software project could use repository inspection and test evidence, while a research project might use milestones, source documents, and review criteria. A business initiative could track deliverables, dependencies, risks, and supporting records.

The exact integrations and verification methods would depend on the project type.

---

## ✅ What Works Today

The current MVP provides a working foundation for project planning, execution tracking, evidence recording, and preliminary GitHub repository inspection.

| Capability | Current implementation |
|---|---|
| User accounts | Registration, sign-in, and sign-out |
| Project management | User-scoped project creation and dashboard |
| Execution planning | Editable, structured project plans |
| Plan validation | Deterministic validation of submitted plans |
| Plan approval | Draft persistence and explicit approval before creating execution records |
| Progress tracking | Milestone completion, task status, and dashboard progress |
| Risk management | Risk records and mitigation information |
| Evidence management | Evidence records with types, descriptions, and optional URLs |
| Repository inspection | GitHub repository inspection and repository-readiness findings |
| Transparency | Findings distinguish available indicators from checks that have not been verified |
| Interface | Responsive dark-themed user interface |

These capabilities form the initial project execution workflow. They should not be confused with the complete long-term product described in the vision.

### 1. Structured project planning

Users can create projects and work with editable execution plans.

The current planning flow uses deterministic starter-plan content rather than live LLM-generated plans. Submitted plans can be validated and saved as drafts before approval.

### 2. Human-controlled execution

Approval is an explicit step. A validated plan does not automatically become an approved execution plan without user action.

Once approved, the system creates persistent milestone and task records that can be tracked independently.

### 3. Progress, risks, and evidence

Users can update task status, track milestones, record risks and mitigation information, and attach evidence records to document progress.

Evidence records currently support descriptions, types, and optional URLs. They are not a comprehensive evidence-upload or verification system.

### 4. Preliminary GitHub repository inspection

ShipShield can connect to and inspect a GitHub repository to identify repository structure, documentation, and readiness-related indicators.

The intention is to help project owners understand what can be observed about a repository without automatically treating every missing indicator as a confirmed failure.

**Important:** Repository inspection is not equivalent to executing the project, running its tests, auditing its security, or proving that it is production-ready.

---

## 🔄 The Proposed Product Workflow

The following describes the intended end-to-end experience. Some steps are supported by the current MVP; others represent planned capabilities.

### Phase 1 — Understand and plan

**1. Define the project**

The user describes the project, its objectives, intended users, constraints, and expected outcome.

**2. Generate a structured blueprint**

The intended AI-assisted system converts the project description into a proposed plan containing:

- Objectives and deliverables
- Milestones and tasks
- Dependencies and prerequisites
- Acceptance criteria
- Risks and mitigation strategies
- Evidence requirements
- Suggested verification methods

*Current status: users can work with editable starter plans and validation. Full AI-generated planning is planned, not implemented.*

**3. Review and approve**

The user reviews the proposed plan, edits it, resolves validation issues, and explicitly approves it before it becomes the execution baseline.

Human approval is intended to remain central to consequential project decisions.

### Phase 2 — Execute and track

**4. Manage work against the plan**

Users update task and milestone status, record risks, and maintain the project as requirements change.

The longer-term product should also help identify blocked work, dependencies that threaten deadlines, and discrepancies between planned and actual progress.

**5. Collect evidence**

Completed work should be associated with useful supporting evidence, such as documents, links, test results, review records, or other relevant artifacts.

The system should distinguish evidence that has merely been supplied from evidence that has actually been checked.

### Phase 3 — Inspect and assess

**6. Connect relevant tools and inspect available information**

For software projects, this could include repository metadata, project documentation, configuration files, test definitions, and—when authorized integrations are available—actual test or CI results.

For non-software projects, the relevant sources would depend on the work being assessed.

**7. Evaluate delivery readiness**

The intended readiness assessment would consider criteria such as:

- Completion of required milestones
- Acceptance criteria and supporting evidence
- Outstanding tasks and dependencies
- Unresolved risks
- Documentation completeness
- Verification results and their provenance
- Explicitly unverified requirements

A readiness assessment should explain *why* a project receives a particular status, rather than provide an unexplained score.

### Phase 4 — Document and deliver

**8. Prepare a delivery package**

The full product is intended to produce a clear summary of what was planned, what was completed, what was verified, what remains unresolved, and what should happen next.

Future documentation tools could propose README changes, release notes, handover documents, or delivery reports. Changes should be reviewable and require appropriate approval before being applied.

**The distinction matters:** the current MVP implements parts of planning, execution tracking, evidence recording, and repository inspection. The complete AI-assisted, evidence-verified delivery workflow remains the product vision.

---

## 🌟 What Makes ShipShield Different?

### Evidence over assumptions

A status label alone is not proof. ShipShield's direction is to connect reported progress with supporting evidence and make verification status explicit.

### Human approval over blind automation

Plans should be editable. Generated recommendations should be reviewable. Significant actions should have clear approval boundaries.

### One project context

The long-term goal is to maintain a coherent understanding of the project's objectives, requirements, work, risks, evidence, and delivery state rather than scattering these across disconnected tools.

### Verification with clear limitations

A missing result should not automatically be reported as a failed result. A repository inspection should not be described as a successful test run. A supplied link should not be described as independently verified evidence unless it has actually been checked.

### Software-first, not software-only

The initial implementation focuses on a practical software-oriented workflow, but the broader model is designed around projects, milestones, tasks, risks, and evidence—concepts that can apply across different domains.

---

## 🧭 Current MVP vs. Full Product

| Area | Current MVP | Intended future capability |
|---|---|---|
| Planning | Editable deterministic starter plans and validation | AI-assisted project understanding and blueprint generation |
| Approval | Explicit approval before execution records are created | Richer review, change history, and approval workflows |
| Execution | Persistent tasks, milestones, and progress tracking | More advanced dependency, blocker, and schedule intelligence |
| Evidence | Typed evidence records with descriptions and optional URLs | Broader evidence collection, validation, and provenance |
| GitHub | Preliminary repository inspection | Deeper repository and development-workflow integrations |
| Testing | Test code and development checks exist; results must be assessed per run and commit | Authorized test execution and verified results |
| Readiness | Preliminary repository findings | Explainable, evidence-based delivery-readiness assessments |
| Documentation | Existing project documentation and repository findings | Reviewable documentation-change proposals and approved updates |
| AI | Full AI planning is not yet implemented | AI-assisted planning, contextual recommendations, and project-aware assistance |
| Project memory | Persistent application data for existing project records | Richer long-term project context and decision history |

This comparison is intended to make the boundary between the current implementation and the proposed product explicit.

---

## 🤖 AI Integration and Hackathon Context

AI-assisted planning is an important part of the ShipShield vision. During the hackathon, however, access to the Alan AI APIs needed for the intended integration was not available to me.

As a result, the current MVP uses deterministic starter-plan content and validation rather than claiming to generate plans through Alan AI or another live LLM integration.

This is an important engineering distinction:

- **Implemented:** editable plan data, validation, draft persistence, and explicit approval.
- **Not yet implemented:** full LLM-driven project-plan generation through Alan AI.
- **Planned:** AI-assisted project understanding, plan generation, contextual recommendations, and richer project-aware workflows.

The absence of that API integration does not mean the current planning foundation is an AI system. It means the MVP establishes the workflow and data structures on which that capability can later be built.

The intended integration should preserve the product's core principles: editable outputs, validation, human review, and transparent reporting.

---

## 🧰 Technology Stack

The current project is built around a Python/Django web application.

| Technology | Role |
|---|---|
| Python | Application logic and backend development |
| Django | Web framework, application structure, authentication, and request handling |
| PostgreSQL | Relational database |
| Psycopg | PostgreSQL database connectivity |
| GitHub API tooling | Repository inspection and integration functionality |
| Django testing / pytest tooling | Automated test development and execution |
| Ruff | Python linting and code-quality checks |
| Gunicorn | Application serving in deployment |
| WhiteNoise | Static-file serving support |
| HTML, CSS, and JavaScript | Web interface |

The codebase is organized as a modular Django application, with areas for projects, planning, evidence, assistant-related functionality, and integrations.

The architecture is intended to support incremental development without requiring a premature move to a distributed system.

---

## 🏗️ Architecture and Engineering Principles

### Modular monolith first

ShipShield currently follows a Django modular-monolith approach. This keeps the application relatively straightforward to develop, test, and deploy while allowing distinct responsibilities to live in separate application modules.

More complex infrastructure should be introduced when the product's requirements justify it.

### Persistent, structured project data

Project plans and execution records should be represented as structured application data rather than relying entirely on free-form text.

This provides a foundation for validation, progress tracking, future integrations, and reporting.

### Validate before executing

The plan workflow separates editing, validation, and approval. This helps prevent unreviewed or invalid plans from being treated as approved execution baselines.

### Be explicit about what was verified

ShipShield should distinguish between:

- **Planned:** a future capability or intended action.
- **Reported:** information supplied by a user or external system.
- **Observed:** information actually retrieved or inspected.
- **Verified:** a specific check was executed and produced a recorded result.
- **Unverified:** available information is insufficient to establish the result.

These categories are especially important for repository health, test results, and delivery readiness.

### Security and ownership

User-specific project operations should respect project ownership and authentication boundaries. Integrations should use appropriately scoped credentials and avoid executing arbitrary code without a deliberate, isolated, and authorized execution design.

### Incremental delivery

The project is being developed in stages: establish the core workflow, validate it, improve its reliability, and then add more advanced AI and integration capabilities.

---

## 🚀 Getting Started

You can explore the deployed MVP or run the application locally.

### Prerequisites

- Python
- PostgreSQL
- Git
- A GitHub account if you want to explore repository integration

### 1. Clone the repository

```bash
git clone https://github.com/SamuelNiiOdoiOddoye/Telix-Shipshield.git
cd Telix-Shipshield
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Use the dependency file included in the repository:

```bash
pip install -r requirements.txt
```

If the dependency-management files have changed in a newer revision, follow the instructions in the current repository instead.

### 4. Configure environment variables

Configure the Django secret key, database connection, allowed hosts, and other settings required by the project's current configuration.

Use any supplied example environment file as the source of truth. Do not commit real secrets, database passwords, or GitHub credentials.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open the local address printed by Django in your terminal.

For the most reliable setup instructions, consult the configuration and dependency files in the repository at the commit you are running.

---

## 🧪 Testing and Verification

Testing is an important part of ShipShield's development, but test availability, local execution, and hosted CI results are different things.

A test file in a repository does not, by itself, prove that the tests passed. Similarly, a failed workflow on a different branch does not establish that the submitted `main` commit failed.

For reproducible verification, record:

1. The exact Git commit being assessed.
2. The command executed.
3. The test or check result.
4. Any relevant environment requirements.
5. Whether the result came from a local run or an automated workflow.

Example commands, depending on the project's installed dependencies and configuration:

```bash
python manage.py check
python manage.py test
```

If pytest is configured for the relevant tests, use the repository's documented pytest command as well.

**Current verification statement:** The project contains test and development-check tooling, but a passing automated CI result should only be claimed when a successful run for the relevant commit is available. Repository inspection by ShipShield does not itself execute the application's test suite.

---

## 🗺️ Roadmap

The roadmap separates the current foundation from future work. It is not a claim that every item below has been completed.

### Foundation and MVP

- [x] Establish the Django application and core project structure.
- [x] Implement user authentication.
- [x] Support project creation and a user-scoped dashboard.
- [x] Support editable execution plans and validation.
- [x] Persist drafts and require explicit approval before creating execution records.
- [x] Track milestones, tasks, and progress.
- [x] Record risks, mitigation information, and evidence.
- [x] Implement preliminary GitHub repository inspection.
- [x] Make repository findings distinguish observed indicators from unverified results.
- [ ] Complete and document a reproducible verification run for the release candidate.
- [ ] Improve consistency between documentation, roadmap status, and the current codebase.

### Next engineering priorities

- [ ] Strengthen automated testing and record reproducible results.
- [ ] Review error handling, authorization boundaries, and integration failure states.
- [ ] Improve repository-inspection accuracy and explainability.
- [ ] Add screenshots and a clear, repeatable product demonstration.
- [ ] Improve the distinction between user-supplied evidence and independently verified results.
- [ ] Document deployment configuration and operational limitations.

### AI and product capabilities

- [ ] Integrate an available AI API for project-plan generation.
- [ ] Validate AI-generated plans before presenting them for approval.
- [ ] Introduce richer project context and decision history.
- [ ] Expand project templates and support for different project types.
- [ ] Develop evidence-aware readiness assessments with explicit criteria.
- [ ] Explore authorized test execution in an isolated environment.
- [ ] Expand repository and development-tool integrations.
- [ ] Propose documentation updates as reviewable changes.
- [ ] Add delivery summaries and handover reports.
- [ ] Develop an audit trail for important project and verification decisions.

### Longer-term direction

- [ ] Support richer integrations with development and project-management tools.
- [ ] Improve dependency, risk, and blocker analysis.
- [ ] Support configurable workflows for teams and organizations.
- [ ] Explore team collaboration and role-based approval workflows.
- [ ] Develop a more comprehensive delivery-assurance system for software and non-software projects.

Roadmap items should be checked off only when the corresponding capability is implemented and its status is supported by the code or documented verification.

---

## ⚠️ Known Limitations

ShipShield is an early-stage MVP, not a fully realized autonomous delivery platform.

Current limitations include:

- **AI planning:** Full LLM-powered plan generation is not implemented in the current MVP.
- **Repository verification:** GitHub inspection does not execute arbitrary repository code, run the project's tests, or independently establish that CI passed.
- **Security assurance:** Repository findings are not a comprehensive security audit.
- **Evidence handling:** Evidence records currently focus on descriptions, types, and optional URLs rather than a full artifact-ingestion and verification pipeline.
- **Delivery readiness:** The complete evidence-based delivery-readiness workflow remains a future capability.
- **Documentation automation:** Automatically proposing, reviewing, and applying README changes is part of the longer-term vision, not a claim about current functionality.
- **Verification status:** Local test results, hosted CI runs, and repository inspection findings must be assessed separately.
- **Production maturity:** The existence of a deployed demonstration does not establish production-grade reliability, scalability, or security.

These limitations define the current development boundary and help guide the next engineering priorities.

---

## 👥 Who ShipShield Is For

### Developers and engineering teams

Organize implementation work, clarify acceptance criteria, track risks, and understand which results have actually been verified.

### Independent builders and founders

Turn ideas into manageable execution plans and communicate project status with clearer supporting evidence.

### Project owners and teams outside software

Apply structured planning, milestone tracking, risk management, and evidence-based progress reporting to work that is not primarily code-driven.

### Reviewers, recruiters, and stakeholders

Understand the intended scope of a project, its current implementation, the evidence available, and the work that remains—without confusing product vision with completed functionality.

---

## 🤝 Contributing and Collaboration

ShipShield is being developed incrementally, and constructive feedback is valuable.

Potential areas for contribution include:

- Django architecture and backend engineering
- Test coverage and reliability
- AI-assisted planning
- GitHub and other tool integrations
- Evidence and verification models
- UI/UX improvements
- Documentation and onboarding
- Security and deployment practices

Before proposing a contribution, please distinguish between existing functionality, a bug in the current implementation, and a feature that belongs to the future roadmap.

Issues and pull requests should explain the problem, expected behavior, and relevant evidence where possible.

---

## 📄 License

A license should be added explicitly before the project is presented as open source for reuse or redistribution. Until a license is included in the repository, do not assume that the source code is available under an open-source license.

---

## 👨🏽‍💻 About the Developer

**Samuel Nii Odoi Oddoye** is a software developer based in Accra, Ghana, building projects across Python, Django, full-stack development, testing, and AI-assisted software workflows.

Telix ShipShield is an exploration of how structured project execution, transparent verification, and AI-assisted decision-making can work together in a practical product.

The current MVP establishes the foundation. The longer-term challenge is to make the system increasingly useful without overstating what it knows, what it has checked, or what it can safely automate.

**Connect and explore:**

- GitHub: [SamuelNiiOdoiOddoye](https://github.com/SamuelNiiOdoiOddoye)
- Project repository: [Telix ShipShield](https://github.com/SamuelNiiOdoiOddoye/Telix-Shipshield)
- Live MVP: [telix-shipshield.onrender.com](https://telix-shipshield.onrender.com)
- Project demo post: [View the demonstration on X](https://x.com/oddoye_samuel/status/2114754319404949536)

---

*Telix ShipShield — a project execution foundation today, with a vision for evidence-aware delivery assurance tomorrow.*
