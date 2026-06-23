# 🌆 City Intelligence Agent

A conversational AI agent that delivers real-time **weather conditions**, **air quality data**, and **breaking news** for any city in the world — powered by a Mistral LLM, LangChain tool-use, and a clean Streamlit interface.

> Ask natural questions like *"What's the air quality in Lahore right now?"* or *"Give me the weather and latest news for Tokyo"* — the agent decides which tools to invoke and synthesizes a coherent response.

---

## Demo

![City Intelligence Screenshot](assets/demo.png)

---

## Features

- **Multi-tool agent** — dynamically routes queries to weather, AQI, or news tools based on intent
- **Middleware layer** — intercepts tool calls before execution, enabling per-call approval or skipping
- **Persistent chat history** — full conversation state maintained in Streamlit session state
- **Dark-mode UI** — custom CSS with card components, responsive layout
- **Cached agent** — `@st.cache_resource` prevents re-initializing the LLM on every rerender

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Mistral (`mistral-small-2506`) via `langchain-mistralai` |
| Agent framework | LangChain (`create_agent`, `@tool`, `wrap_tool_call`) |
| Weather & AQI | OpenWeatherMap REST API |
| News retrieval | Tavily Search API |
| Frontend | Streamlit |
| Environment | `python-dotenv` |

---

## Skills Demonstrated

- **LLM agent design** — tool binding, system prompts, multi-step reasoning
- **LangChain internals** — `ToolMessage`, `RunnableLambda`, middleware via `wrap_tool_call`
- **API integration** — OpenWeatherMap (current weather + geocoding + air pollution endpoints), Tavily
- **State management** — Streamlit session state for chat history and tool approval flags
- **Python best practices** — decorators, environment variable management, clean separation of concerns
- **UI development** — custom CSS injection in Streamlit, form handling, dynamic rendering

---

## Project Structure

```
city-intelligence-agent/
├── app.py              # Main application — agent, tools, middleware, UI
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- API keys for OpenWeatherMap, Tavily, and Mistral

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/city-intelligence-agent.git
cd city-intelligence-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
OPENWEATHER_API_KEY=your_openweathermap_api_key
TAVILY_API_KEY=your_tavily_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

**Where to get them:**
- OpenWeatherMap → https://openweathermap.org/api (free tier is sufficient)
- Tavily → https://app.tavily.com (free tier available)
- Mistral → https://console.mistral.ai

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## How It Works

```
User query
    │
    ▼
Mistral LLM (reasoning + tool selection)
    │
    ├── get_weather(city)       → OpenWeatherMap /weather
    ├── get_air_quality(city)   → OpenWeatherMap /geo + /air_pollution
    └── get_news(query)         → Tavily Search
    │
    ▼
tool_call_middleware             ← intercepts each call; can approve/skip
    │
    ▼
Synthesized natural language response
    │
    ▼
Streamlit chat UI
```

The agent uses LangChain's `create_agent` with a `wrap_tool_call` middleware that checks session state before allowing any tool to execute. This makes it straightforward to add human-in-the-loop approval flows.

---

## Example Queries

- `What's the weather in Karachi today?`
- `Is the air quality safe in Delhi right now?`
- `Give me the latest news about Pakistan`
- `Tell me everything about London — weather, AQI, and news`

---

## API Reference

### Tools

**`get_weather(city: str) → str`**  
Calls OpenWeatherMap's `/data/2.5/weather` endpoint and returns a human-readable description of current conditions and temperature.

**`get_air_quality(city: str) → str`**  
Geocodes the city using `/geo/1.0/direct`, then fetches the AQI from `/data/2.5/air_pollution`. Returns a labeled quality level (Good / Fair / Moderate / Poor / Very Poor).

**`get_news(query: str) → str`**  
Queries Tavily with `max_results=5` and returns a list of article titles with URLs.

---

## Roadmap

- [ ] Add 5-day weather forecast tool
- [ ] Streaming responses via `st.write_stream`
- [ ] Per-tool human approval UI (approve/skip buttons)
- [ ] Docker support
- [ ] Deploy to Streamlit Community Cloud

---

## License

MIT — see [LICENSE](LICENSE) for details.
