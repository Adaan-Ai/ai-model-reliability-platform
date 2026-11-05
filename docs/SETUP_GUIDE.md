# Complete Installation & Local Setup Guide

Follow this step-by-step guide to configure the database, install dependencies, seed real business data, and run both backend and frontend servers.

---

## 1. Prerequisites

Ensure the following runtimes are installed on your system:
- **Python:** 3.10, 3.11, or 3.12 (`python --version`)
- **Node.js:** 18+ or 20+ (`node --version`)
- **npm:** 9+ or 10+ (`npm --version`)
- **MySQL Server:** 8.0 (`mysql --version`)

---

## 2. MySQL Database Setup

1. Open your terminal or MySQL Workbench and log in to MySQL:
   ```bash
   mysql -u root -p
   ```

2. Execute the schema script to create `ai_model_reliability` and all 12 core tables:
   ```sql
   source database/schema.sql;
   ```
   *(Or via command line)*:
   ```bash
   mysql -u root -p < database/schema.sql
   ```

3. Apply the 4 analytical reporting views:
   ```bash
   mysql -u root -p < database/views.sql
   ```

---

## 3. Backend Setup & Configuration

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a local `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if your MySQL password or host differs:
   ```env
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=ai_model_reliability
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Populate realistic demo datasets and execute real Scikit-learn evaluations:
   ```bash
   python seed_data.py
   ```
   *This command creates users, data sources, generates 2 business datasets (Bank Fraud & Customer Churn) across versions, executes 24 data quality checks, trains 5 Scikit-learn classification models, serializes Joblib artifacts, and calculates real drift and reliability scores.*

5. Run the automated backend test suite:
   ```bash
   python -m pytest
   ```
   *(All 16 tests should pass cleanly!)*

6. Start the FastAPI backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The API will be available at:
   - **API Root:** `http://localhost:8000`
   - **Interactive Swagger Docs:** `http://localhost:8000/docs`
   - **Health Check:** `http://localhost:8000/health`

---

## 4. Frontend Setup & Launch

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Verify the production build:
   ```bash
   npm run build
   ```

4. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   Open your browser at:
   - **Platform Dashboard:** `http://localhost:5173`

---

## 5. Testing the End-to-End Workflow

1. Open `http://localhost:5173` to view live KPI cards and trend charts populated directly from MySQL.
2. Navigate to **Datasets** &rarr; click **Upload New Dataset** &rarr; choose a CSV file.
3. Observe automatic column profiling, version creation, and quality checks.
4. Navigate to **Evaluations** &rarr; click **Launch New Evaluation** &rarr; select a model, dataset version, and target column (`is_fraud` or `churn`).
5. Observe the live Scikit-learn execution, confusion matrix, PSI drift breakdown, and updated reliability rating!
