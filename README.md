# SensAI

[![codecov](https://codecov.io/gl/hvacademy/sensai-ai/branch/main/graph/badge.svg)](https://codecov.io/gl/hvacademy/sensai-ai)

SensAI is an AI-first Learning Management System (LMS) which enables educators to teach smarter and reach further. SensAI coaches students through questions that develop deeper thinking—just like you would, but for every student and all the time.

This repository contains both backend (Python/FastAPI) and frontend (React) code for SensAI.  
- **Backend**: Handles AI chat, user management, tasks, scoring, and more.
- **Frontend**: User interface for educators and learners.

---

## Setup

### Backend (Python/FastAPI)

1. **Clone the repository**  
   ```bash
   git clone https://github.com/08sarthak/Hyperverge-Team-Error.git
   cd Hyperverge-Team-Error/sensai-ai
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables**  
   - Copy `.env.example` to `.env` and fill in required settings (DB connection, API keys, etc.).

4. **Database setup**  
   - Set up your database as per the environment file.
   - Run migrations if available (see project docs for details).

5. **Run the backend server**  
   ```bash
   uvicorn src.api.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend (React/Next.js)

See the `sensai-frontend` directory for complete instructions.  
Basic steps:
1. Ensure backend is running.
2. Install Node.js (if not already).
3. Clone and set up frontend:
   ```bash
   cd ../sensai-frontend
   npm ci
   cp .env.example .env.local
   # Edit .env.local as needed (Judge0 keys, OAuth, etc.)
   npm run dev
   ```
   App will be available at `http://localhost:3000`.

---

## How it works

### Backend

- Built with **FastAPI**, the backend serves RESTful endpoints for all core LMS and AI features.
- **Key modules/routes include:**
  - `/auth`: Authentication (sign-in, sign-up, JWT tokens, etc.)
  - `/users`, `/organizations`, `/cohorts`, `/courses`, `/milestones`, `/scorecards`, `/tasks`, `/lessonplan`, `/student`, etc.: User, organization, and educational content management.
  - `/ai` and `/chat`: AI-driven interactions, including question answering, chat coaching, and real-time feedback.
  - `/file`: File upload and download.
  - `/code`: Code execution and evaluation (uses Judge0 or similar).
- **AI Features**:  
  AI chat endpoints use modern language models to analyze student input and provide tailored feedback. The system can route tasks to different LLMs (e.g., GPT-4o for general, O3 for reasoning tasks).
- **Middleware**:  
  - CORS enabled for frontend-backend interaction.
  - Bugsnag integration for error monitoring.
- **Testing**:  
  Uses `pytest` for API and logic testing. Run `./run_tests.sh` for full test and coverage report.

### Frontend

- Built with React (Next.js).
- Connects to backend for authentication, course/task management, and AI chat.
- Includes components like `LearningMaterialViewer`, interactive chat, and dashboards.

---

## Testing

**Backend:**
```bash
pip install -r requirements-dev.txt
./run_tests.sh
# Coverage report: coverage_html/index.html
```

**Frontend:**
```bash
npm run test:ci
# (Optional) Upload coverage to Codecov
```

---

## Contributing

See [CONTRIBUTING.md](sensai-ai/docs/CONTRIBUTING.md) for details.

---

## Community

Join our [WhatsApp group](https://chat.whatsapp.com/LmiulDbWpcXIgqNK6fZyxe) for discussions around AI + Education.

---

## Documentation

For more, see [docs.sensai.hyperverge.org](https://docs.sensai.hyperverge.org) or the in-repo docs folder.

---

## License

GNU Affero General Public License. See `LICENSE` for details.

---

## Roadmap

Check out our [public roadmap](https://hyperverge.notion.site/fa1dd0cef7194fa9bf95c28820dca57f?v=ec52c6a716e94df180dcc8ced3d87610) and let us know what you think we should build next!
