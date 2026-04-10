# NETSCOPE

Network port scanner with real-time CVE detection, built with FastAPI + React.

![NETSCOPE](https://github.com/Lautarorosa/netscope-/raw/main/static/assets/preview.png)

## Features

- Real-time port scanning via WebSocket
- Banner grabbing and CVE signature matching
- Severity classification (CRITICAL / HIGH / MEDIUM / LOW)
- Scan history with SQLite
- PDF report export
- React + TypeScript frontend

## Stack

| Layer    | Tech                        |
|----------|-----------------------------|
| Backend  | FastAPI, Uvicorn, Python 3  |
| Frontend | React, TypeScript, Vite     |
| Database | SQLite                      |
| Reports  | ReportLab                   |

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Lautarorosa/netscope-.git
cd netscope-
```

### 2. Backend

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend (dev)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

### Production build

```bash
cd frontend
npm run build
```

Then just run the backend — FastAPI serves the built frontend from `static/`.

## Usage

1. Enter a target IP or hostname
2. Set port range and speed
3. Click **Start Scan**
4. View results in real-time, export as PDF
