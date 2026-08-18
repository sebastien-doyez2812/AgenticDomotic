from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tools.ambiance import set_musique
from tools.plant_watering import plant_watering
from state import State
from prompt.system import SYSTEM_PROMPT

tools = [set_musique, plant_watering]
model = ChatOllama(model="llama3.2:latest ").bind_tools(tools)

def call_model(state: State):
    messages = SYSTEM_PROMPT + state["graph_state"]
    response = model.invoke(messages)
    return {"graph_state": messages + [response]}

workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

app = workflow.compile()