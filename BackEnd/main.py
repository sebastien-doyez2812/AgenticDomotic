from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage
from tools.ambiance import set_music
from tools.plant_watering import plant_watering
from state import State
from prompt.system import SYSTEM_PROMPT


def agent_factory(custom_model = None):
    tools = [set_music, plant_watering]
    model = custom_model or ChatOllama(model="gemma4:latest ").bind_tools(tools)

    def call_model(state: State):
        messages = [SYSTEM_PROMPT] + state["graph_state"]
        response = model.invoke(messages)
        return {"graph_state": state["graph_state"] + [response]}

    workflow = StateGraph(State)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools, messages_key="graph_state"))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        lambda state: tools_condition(state, messages_key="graph_state"),
        {"tools": "tools", "__end__": END},
    )

    workflow.add_edge("tools", "agent")

    app = workflow.compile()
    return app

# To test the back end in real life:
if __name__ == "__main__":
    app = agent_factory()
    inputs = {
    "graph_state": [
        HumanMessage(content="Pourrais-tu arroser les plantes s'il te plaît ?")
    ]
    }
    print("--- Beginning of the execution: ---")
    # app.invoke(inputs)
    for event in app.stream(inputs):
        for node_name, node_output in event.items():
            print(f"\n[Node executed : {node_name}]")
            print("Output :", node_output)
    print("\n--- End of execution ---")