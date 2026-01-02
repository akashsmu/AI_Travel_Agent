# AI Travel Agent

A production-grade AI travel planning system powered by **LangGraph**, **SerpAPI**, and **SingleStore**, with a premium **React (Next.js)** frontend.

## Features

- 🔍 **Real-time Search**: Google Flights & Hotels via SerpAPI
- 📝 **AI Itinerary Generation**: Day-by-day travel plans
- 💾 **Persistent State**: SingleStore for caching and real-time updates
- 🎨 **Premium UI**: Modern React interface with real-time streaming
- 📊 **Production-Ready**: Comprehensive logging, error handling, and schemas

## Architecture

```
┌─────────────┐
│  React/Next │───► FastAPI Server ───► LangGraph
└─────────────┘         │                   │
                        │                   ▼
                        │          Agents (Search, Itinerary)
                        │                   │
                        ▼                   ▼
                   SingleStore ◄────── SerpAPI Tools
```

## Setup

### 1. Prerequisites

- Python 3.9+
- Node.js 18+
- SingleStore Database (cloud or self-hosted)
- API Keys:
  - OpenAI API Key
  - SerpAPI Key

### 2. Backend Setup

```bash
cd AI-Travel-Agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys:
# OPENAI_API_KEY=sk-...
# SERPAPI_API_KEY=...
# SINGLESTORE_URL=admin:password@host:port/database_name

# Initialize database
python database/init_db.py
```

### 3. Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Run the Application

**Terminal 1 - Backend API:**
```bash
source venv/bin/activate
python -m uvicorn api.server:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

Visit: `http://localhost:3000`

## Project Structure

```
AI-Travel-Agent/
├── agents/
│   ├── tools/
│   │   └── serp_tools.py       # SerpAPI wrappers
│   ├── search_agent.py         # Hotel search
│   ├── flight_api_agent.py     # Flight search
│   ├── itinerary_agent.py      # Itinerary generation
│   └── ...
├── database/
│   ├── init_db.py              # Schema initialization
│   ├── singlestore_client.py   # DB connection
│   ├── cache.py                # Cache lookups
│   └── store_results.py        # Data persistence
├── api/
│   └── server.py               # FastAPI endpoints & WebSocket
├── utils/
│   └── logger.py               # Centralized logging
├── graph.py                    # LangGraph flow definition
├── state.py                    # State schema
├── main.py                     # CLI interface
└── web/                        # Next.js frontend
    └── ...
```

## API Endpoints

### HTTP

- `POST /plan` - Run full trip planning
  ```json
  {
    "origin": "SFO",
    "destination": "NYC",
    "start_date": "2024-05-10",
    "end_date": "2024-05-15"
  }
  ```

### WebSocket

- `WS /ws/chat` - Stream real-time updates

## Database Schema

### `flights`
- `id`, `airline`, `origin`, `destination`, `price`, `url`, `details` (JSON), `created_at`

### `accommodations`
- `id`, `name`, `city`, `country`, `price_per_night`, `rating`, `bedrooms`, `url`, `description`, `created_at`

### `trip_plans`
- `id`, `origin`, `destination`, `start_date`, `end_date`, `itinerary_text`, `created_at`

## Logging

All agents and database operations use centralized logging (`utils/logger.py`):
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failures with stack traces

## Development

### Testing Backend
```bash
python test_backend.py
```

### Extending Agents

Add new nodes to `graph.py`:
```python
from agents.my_new_agent import my_function

graph.add_node("my_node", my_function)
graph.add_edge("previous_node", "my_node")
```

## License

MIT
