from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, HumanMessage
from tools.ambiance import set_music
from tools.plant_watering import plant_watering
from state import State
from prompt.system import SYSTEM_PROMPT
import speech_recognition as sr
import pyttsx3


def agent_factory(custom_model = None):
    tools = [set_music, plant_watering]
    model = custom_model or ChatOllama(model="gemma4:latest").bind_tools(tools)

    def call_model(state: State):
        messages = [SYSTEM_PROMPT] + state["graph_state"]
        response = model.invoke(messages)
        return {"graph_state": [response]}

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

def make_agent_speak(engine, conversation_state):
    if conversation_state["graph_state"]:
        last_response = conversation_state["graph_state"][-1]
        if isinstance(last_response, AIMessage):
            print("Agent response:", last_response.content)
            engine.say(last_response.content)
            engine.runAndWait()

if __name__ == "__main__":
    app =  agent_factory()
    engine = pyttsx3.init()
    r = sr.Recognizer()

    conversation_state = {"graph_state": []}

    while(True):
        
        with sr.Microphone() as source:
            print("Agent is listening...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

        try:
            user_input = r.recognize_google(audio, language="fr-FR")
            print("You said :", user_input)

            inputs = {
                "graph_state": [
                    HumanMessage(content=user_input)
                ]
            }
            print("--- Beginning of execution ---")

            config = {"recursive_limit": 3, "max_iterations": 2}
            for event in app.stream(inputs, config= config):
                for node_name, node_output in event.items():
                    # print(f"\n[Node executed : {node_name}]")
                    # print("Output :", node_output)
                    if "graph_state" in node_output:
                        conversation_state = node_output  # Update the conversation state with the latest output
                          # Update the conversation state with the latest output
            print("\n--- End of execution ---")

            make_agent_speak(engine, conversation_state)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            print(f"Error occurred while requesting results from Google Speech Recognition; {e}")
        except KeyboardInterrupt:
            print("Exiting the program.")
            break