import os
import sys
import json
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

from rag.retriever import search_knowledge_base as rag_search
from leads.capture import capture_lead as save_lead

# ── State ─────────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: List[BaseMessage]
    phone_number: str
    lead_captured: bool

# ── Tools ─────────────────────────────────────────────────────────────────────
@tool
def search_spa_knowledge(query: str) -> str:
    """Search Well Beings spa info: services, pricing, FAQs, location, hours."""
    return rag_search(query)

@tool
def search_internet(query: str) -> str:
    """Search internet for real-time info: weather, transport, nearby places."""
    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = tavily.search(query, max_results=3)
        output = []
        for r in results["results"]:
            output.append(f"{r['title']}: {r['content'][:300]}")
        return "\n\n".join(output)
    except Exception as e:
        return f"Search failed: {str(e)}"

tools = [search_spa_knowledge, search_internet]
tools_by_name = {t.name: t for t in tools}

# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatOllama(model="mistral", temperature=0.3)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are the AI receptionist for Well Beings, a luxury spa in Dubai Marina, UAE. You handle WhatsApp enquiries.

Your personality: warm, professional, helpful.

Tool usage rules:
- Questions about spa services, prices, booking, location, hours → use search_spa_knowledge
- Questions about weather, transport, nearby places → use search_internet

Keep replies short and conversational. Always suggest a next step. Prices are in AED."""

# ── Nodes ─────────────────────────────────────────────────────────────────────
def call_agent(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": state["messages"] + [response]}

def run_tools(state: AgentState):
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        result = tools_by_name[name].invoke(args)
        tool_messages.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )

    return {"messages": state["messages"] + tool_messages}

def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

# ── Graph ─────────────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_agent)
    graph.add_node("tools", run_tools)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    return graph.compile()

agent_graph = build_graph()

def run_agent(message: str, phone_number: str, history: list = None) -> str:
    history = history or []

    # Lead capture via pattern matching (Mistral tool calling is unreliable for this)
    name_match = re.search(
        r"\b(?:I(?:'m| am)\s+|my name is\s+)([A-Z][a-z]+)", message
    )
    booking_keywords = ["book", "reserve", "appointment", "schedule", "want to come", "i'd like"]
    has_booking_intent = any(kw in message.lower() for kw in booking_keywords)

    state = {
        "messages": history + [HumanMessage(content=message)],
        "phone_number": phone_number,
        "lead_captured": False
    }

    result = agent_graph.invoke(state)

    # Capture lead if name + booking intent detected
    if name_match and has_booking_intent:
        name = name_match.group(1)
        save_lead(name=name, intent=message, phone=phone_number)
        print(f"[Lead captured: {name}]")

    return result["messages"][-1].content