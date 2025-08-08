# SensAI Architectural Design Brief (Backend & AI Workflows)

## Overview

SensAI is an AI-driven Learning Management System (LMS) designed to personalize learning experiences for students and empower educators with intelligent planning tools. The architecture harmonizes modern backend practices with advanced AI-driven workflows, ensuring modularity, scalability, and adaptability for evolving educational needs.

---

## Key Objectives

- Deliver personalized, standards-aligned lesson plans using Retrieval-Augmented Generation (RAG) and LLMs.
- Conduct adaptive student assessments that inform individualized instruction.
- Enable modular, parallel, and extensible workflow orchestration.
- Maintain robust validation, review, and traceability for all generated educational content.

---

## Core Architectural Components

### 1. Backend Platform

- Built on **Python FastAPI**, chosen for async support, high throughput, and strong API typing.
- **Modular route organization:** clear separation between student, educator, and AI/lessonplan endpoints.
- **MongoDB** is used for flexible storage of content (e.g., chapters, topics), assessment data, and plan artifacts.

### 2. AI & Orchestration Layer

- Uses **GPT-4o** and similar LLMs for all generative and analysis tasks: lesson plan outlining, detailed expansion, student assessment, and automated review.
- RAG (Retrieval-Augmented Generation) pipelines combine semantic/document retrieval with LLM synthesis to ground outputs in user-supplied or curated content.
- **LangGraph** is used to model workflows as directed graphs (nodes: content fetch, prompt build, LLM call, review, etc.).
- **Parallelization:** Independent nodes are parallelized to minimize latency, supporting future scaling and complex compositions.

### 3. Personalization Engine

- Student assessment agent interacts via chat to gather academic background, learning style, confidence, habits, and preferences.
- Assessment results directly parameterize lesson plan generation—adapting objectives, instructional methods, content sequence, and difficulty.
- Reading level estimation, duplicate detection, and learning style adaptation are handled by specialized prompts and post-processing.

### 4. Data & Process Management

- Each user interaction (assessment, plan, review) is tracked as a **thread**; all states and outputs are persisted for history, auditing, and debugging.
- AI outputs are validated for schema compliance and correctness before being served to users.
- Versioning of generated plans and reviews ensures traceability and reproducibility.

### 5. Quality Assurance Pipeline

- Automated LLM-based review agent assesses lesson plans for:
  - Reading level appropriateness, clarity, bias, completeness, compliance (NEP 2020/NCF 2023/SQAAF), and engagement.
- Plans failing review trigger automated revision cycles, returning to educators only when quality criteria are met.

### 6. Extensibility & Maintenance

- Each workflow node is a well-defined function, facilitating targeted testing, easy updates, and plug-and-play extension (e.g., adding quiz generation or new compliance standards).
- Prompt templates are versioned and centrally logged for monitoring and future tuning.
- The system is designed to integrate emerging LLMs or retrieval mechanisms with minimal refactoring.

---

## Repository Structural Diagram

Below is the complete directory and file structure for SensAI (`Hyperverge-Team-Error`). This diagram covers both backend (Python/FastAPI) and frontend (TypeScript/React/Next.js) code, as well as documentation and configuration files.

```plaintext
Hyperverge-Team-Error/
│
├── .env
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── design_brief.md
├── prompt_log.txt
│
├── docs/
│   ├── CONTRIBUTING.md
│   └── ... (other documentation files)
│
├── sensai-ai/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── run_tests.sh
│   ├── .env.example
│   ├── .gitignore
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_lessonplan_routes.py
│   │   ├── test_student_assessment.py
│   │   └── ... (other test files)
│   └── src/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py
│       │   │   ├── lessonplan.py
│       │   │   ├── student.py
│       │   │   └── ... (other route files)
│       │   ├── utils/
│       │   │   ├── __init__.py
│       │   │   ├── lessonplan/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── prompt.py
│       │   │   │   ├── rag/
│       │   │   │   │   ├── __init__.py
│       │   │   │   │   └── prompt_rag.py
│       │   │   ├── student/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── student_assessment_agent.py
│       │   │   │   ├── student_lesson_agent.py
│       │   │   └── ... (other utility files)
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   └── ... (Pydantic/ORM models)
│       │   └── ... (other API core code)
│       └── ... (other backend code)
│
├── sensai-frontend/
│   ├── .env.example
│   ├── .gitignore
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── public/
│   │   └── ... (static assets)
│   ├── src/
│   │   ├── components/
│   │   │   └── ... (React components)
│   │   ├── pages/
│   │   │   └── ... (Next.js pages)
│   │   ├── utils/
│   │   │   └── ... (utility functions)
│   │   └── ... (other frontend code)
│   └── ... (other frontend configs/files)
│
└── ... (any additional files or folders in the root)
```

**Legend:**
- `__init__.py`: Python package/module initializers.
- `...`: Indicates additional files or subdirectories not listed individually for brevity.

---

## Summary

SensAI’s backend and AI architecture meld graph-based workflow orchestration, robust data management, and advanced LLM integration to deliver a scalable, maintainable, and highly personalized LMS. The architecture is positioned for rapid extension as education and AI technology evolve, while keeping educator and student needs central.
