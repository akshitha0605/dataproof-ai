# DATAPROOF AI

### *"Ask your data. Get a proven answer."*

**DATAPROOF AI** is a universal, proof-carrying AI data analyst platform built to eliminate LLM numerical hallucinations. Instead of estimating or fabricating answers from memory, **DATAPROOF AI** dynamically generates Python/Pandas code, executes it against the user's uploaded dataset inside a secure sandbox runtime, and verifies the calculation before returning the answer alongside auditable proof code and source-of-truth evidence.

---

## 🎯 Problem Statement

Traditional conversational AI chatbots suffer from critical limitations when analyzing datasets:
1. **Hallucinations & Inaccurate Math**: LLMs generate plausible-sounding numbers instead of executing exact calculations.
2. **Opaque Reasoning**: Users cannot inspect how a calculated metric or entity was derived.
3. **Overcomplicated Interfaces**: Existing analytical software overwhelms users with dozens of complex dashboards, agent traces, and multi-tab workflows.

**DATAPROOF AI** solves this by enforcing a single, streamlined user experience:

$$\text{UPLOAD} \longrightarrow \text{ASK} \longrightarrow \text{ANSWER} \longrightarrow \text{PROOF}$$

The complexity exists internally in the backend engine, while the user interface remains minimal, calm, and actionable.

---

## ✨ Key Features

- **⚡ 100% Dynamic Execution**: Zero hardcoded dataset names, column names, expected answers, or domain-specific formulas.
- **🛡️ Proof-Carrying Answer Screen**: Returns clean answers with a `VERIFIED ✓` badge emitted only after strict sandbox code execution passes.
- **👤 Entity + Value Resolution**: "Who" and entity-seeking questions automatically resolve and return both the entity name AND the value (e.g. `'Computer Science' with 95.00` or `Alice: 95,000`).
- **📊 Mean Aggregation Enforcement**: Questions asking for average/mean dynamically execute `.mean()` instead of `.sum()`.
- **🔍 Expandable Evidence & Proof Code**:
  - **`[ View Evidence ]`**: Interactive, searchable table displaying supporting rows computed directly from dataset memory (with CSV export).
  - **`[ View Proof Code ]`**: Exact, auditable Python/Pandas code executed, accompanied by raw execution output (`✓ Code executed successfully`).
- **🛑 Anti-Hallucination Refusal (`CANNOT DETERMINE`)**: Refuses to fabricate answers when required data columns do not exist in the dataset.
- **❓ Ambiguity Clarification (`CLARIFICATION REQUIRED`)**: Prompts the user with column selection buttons when multiple numerical fields match a generic query.
- **🌙 Sleek SPA & Dark/Light Mode**: Single-page application built with modern typography, subtle micro-animations, responsive design, and light/dark theme toggle.

---

## 📁 Supported File Formats

- **CSV** (`.csv`)
- **Excel** (`.xlsx`, `.xls`) with Multi-Sheet selection
- **JSON Records** (`.json`)
- **TSV** (`.tsv`)

---

## 🛠️ Technologies Used

### Backend
- **Python 3.10+** (FastAPI, Uvicorn)
- **Pandas & NumPy** (Data processing and memory execution)
- **OpenPyXL** (Excel parsing)
- **SQLite** (Dataset profiling and analysis record storage)
- **Google GenAI SDK** (`google-genai` / Gemini 2.5 Flash API)

### Frontend
- **React 18** (Functional components, Hooks)
- **Vite 6** (Blazing fast build tool & dev server)
- **Tailwind CSS v3** (Custom design tokens, glassmorphism, responsive utilities)
- **Lucide React** (Modern clean iconography)

### Testing
- **Pytest** & FastAPI **TestClient** (Automated backend & end-to-end integration tests)

---

## 🤖 Gemini API Usage

DATAPROOF AI integrates Google's Gemini API via the official `google-genai` SDK:
- **Question Planner Agent (`question_planner.py`)**: Translates natural-language user queries into structured JSON analysis plans (`intent`, `metrics`, `operations`, `group_by`, `sort`).
- **Code Generator Agent (`code_generator.py`)**: Converts the analysis plan and discovered schema into minimal, deterministic Python/Pandas code targeting `df`.
- **Heuristic Fallback Engine**: If no Gemini API key is configured or the API is unreachable, the platform seamlessly activates an intelligent heuristic planner and code generator, ensuring zero downtime.

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory (refer to `.env.example`):

```env
# Gemini API Key (Optional - Heuristic engine active if unset)
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Backend Server Configuration
HOST=127.0.0.1
PORT=8000
```

---

## 🚀 Installation & Running Instructions

### 1. Prerequisites
- **Python**: `v3.10` or higher
- **Node.js**: `v18` or higher

### 2. Backend Setup & Run

```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI Backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Backend API will be running at `http://127.0.0.1:8000`.

### 3. Frontend Setup & Run

```bash
# Open a new terminal and navigate to frontend folder
cd frontend

# Install Node dependencies
npm install

# Run Vite Development Server
npm run dev
```
Open your browser at `http://localhost:3000`.

---

## 🧪 Running Automated Tests

Run the full end-to-end pytest test suite covering file upload, dynamic profiling, Pandas code execution, entity+value resolution, average aggregation, ambiguity handling, and refusal logic:

```bash
cd backend
python -m pytest tests -v
```

---

## 💡 Sample Usage

1. **Upload Dataset**: Drag and drop `students.csv` into the upload zone.
2. **Ask Question**: Type *"Which department has the highest average Programming marks?"*
3. **Click Analyze**:
   - System calculates mean Programming mark per department.
   - Returns: **`'CS' with 95.00 (highest average Programming)`**.
   - Badge: **`✓ VERIFIED`**.
4. **Inspect Proof**:
   - Click **`[ View Evidence ]`** to view department mean breakdown table.
   - Click **`[ View Proof Code ]`** to view exact Pandas code executed:
     ```python
     grouped = working_df.groupby('Department')['Programming'].mean().reset_index()
     grouped = grouped.sort_values(by='Programming', ascending=False)
     top_row = grouped.iloc[0]
     ```

---

## 👥 Team & Project Information

- **Project**: DATAPROOF AI — Universal Proof-Carrying AI Data Analyst
- **License**: MIT
