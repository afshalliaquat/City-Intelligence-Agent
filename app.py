from dotenv import load_dotenv
load_dotenv()

import os
import requests
from langchain_core.messages import ToolMessage
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from tavily import TavilyClient
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.runnables import RunnableLambda
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="City Intelligence", page_icon="🌆", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .main-title { 
        font-size: 2.2rem; font-weight: 700; color: #ffffff;
        text-align: center; margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem; color: #8b8fa8;
        text-align: center; margin-bottom: 2rem;
    }
    .tool-card {
        background: #1e2130; border-radius: 10px;
        padding: 0.8rem 1rem; margin: 0.4rem 0;
        border-left: 4px solid #4f8ef7;
        color: #d0d4e8; font-size: 0.9rem;
    }
    .response-box {
        background: #1e2130; border-radius: 12px;
        padding: 1.2rem 1.5rem; margin-top: 1rem;
        border: 1px solid #2e3250; color: #e8eaf6;
        font-size: 1rem; line-height: 1.6;
    }
    .chat-user {
        background: #2a2d3e; border-radius: 10px;
        padding: 0.7rem 1rem; margin: 0.5rem 0;
        color: #a0c4ff; font-size: 0.95rem;
    }
    .chat-bot {
        background: #1a1d2e; border-radius: 10px;
        padding: 0.7rem 1rem; margin: 0.5rem 0;
        color: #e8eaf6; font-size: 0.95rem;
        border-left: 3px solid #4f8ef7;
    }
    div[data-testid="stButton"] button {
        background: #4f8ef7; color: white;
        border: none; border-radius: 8px;
        font-weight: 600; width: 100%;
    }
    div[data-testid="stButton"] button:hover { background: #3a7bd5; }
</style>
""", unsafe_allow_html=True)

# ── Tools ─────────────────────────────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """Return the current weather of the city"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    data = requests.get(url).json()
    if data["cod"] != 200:
        return f"Error: {data['message']}"
    return f"The current weather in {city} is {data['weather'][0]['description']} with a temperature of {data['main']['temp']}°C."

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def get_news(query: str) -> str:
    """Return the latest news articles related to the query"""
    results = tavily_client.search(query, max_results=5)['results']
    return "\n".join([f"{r['title']}: {r['url']}" for r in results])

@tool
def get_air_quality(city: str) -> str:
    """Return the current air quality index of the city"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    geo = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}").json()
    if not geo:
        return f"City '{city}' not found."
    lat, lon = geo[0]["lat"], geo[0]["lon"]
    data = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}").json()
    aqi = data["list"][0]["main"]["aqi"]
    labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
    return f"The air quality in {city} is {labels.get(aqi, 'Unknown')} (AQI: {aqi})."

# ── Middleware ────────────────────────────────────────────────────────────────
if "pending_tools" not in st.session_state:
    st.session_state.pending_tools = []

@wrap_tool_call
def tool_call_middleware(request, handler):
    tool_name = request.tool_call["name"]
    approval_key = f"approve_{request.tool_call['id']}"
    if st.session_state.get(approval_key) == "no":
        return ToolMessage(
            content=f"Tool call '{tool_name}' skipped by user.",
            tool_call_id=request.tool_call["id"])
    return handler(request)

# ── Agent ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def build_agent():
    llm = ChatMistralAI(model="mistral-small-2506")
    agent = create_agent(
        llm,
        tools=[get_weather, get_news, get_air_quality],
        system_prompt="You are a helpful assistant that provides weather, air quality and news. Use tools when needed.",
        middleware=[tool_call_middleware]
    )
    extract_response = RunnableLambda(lambda result: result["messages"][-1].content)
    return agent | extract_response

chain = build_agent()

# ── Session state ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🌆 City Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Weather · Air Quality · Latest News</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.markdown('<div class="tool-card">🌤️ Weather</div>', unsafe_allow_html=True)
col2.markdown('<div class="tool-card">🌫️ Air Quality</div>', unsafe_allow_html=True)
col3.markdown('<div class="tool-card">📰 News</div>', unsafe_allow_html=True)

st.divider()

for chat in st.session_state.chat_history:
    st.markdown(f'<div class="chat-user">🧑 {chat["user"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chat-bot">🤖 {chat["bot"]}</div>', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask about any city...", placeholder="e.g. Tell me the weather and news of Karachi")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    with st.spinner("Thinking..."):
        response = chain.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })
    st.session_state.chat_history.append({"user": user_input, "bot": response})
    st.markdown(f'<div class="chat-user">🧑 {user_input}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="response-box">🤖 {response}</div>', unsafe_allow_html=True)

if st.session_state.chat_history:
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
