import asyncio
import json
import os
from fastapi.responses import FileResponse
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from tools.ambiance import set_music
from tools.plant_watering import plant_watering
from state import State
from prompt.system import SYSTEM_PROMPT
import speech_recognition as sr
import pyttsx3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from queue import Queue
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

class BasicInteraction(BaseModel):
    user_message: str
    ai_message: str

def agent_factory(custom_model = None):
    model = custom_model or ChatOllama(model="gemma4:latest")

    def intent_condition(state: State): 
        last_message = state["graph_state"][-1].content

        if last_message:
            ROUTER_PROMPT = SystemMessage(content="""Tu es un routeur domotique. Analyse la demande et réponds UNIQUEMENT par un JSON valide sous la format :
            {"intent": "music" | "watering" | "chat"}
            - "music" si l'utilisateur veut lancer de la musique, de l'ambiance, des sons.
            - "watering" si l'utilisateur veut arroser les plantes ou lancer la pompe.
            - "chat" pour toute autre discussion ou question générale.""")

            response = model.invoke([ROUTER_PROMPT] + state["graph_state"])
            try:
                content = response.content.replace("```json", "").replace("```", "").strip()
                decision = json.loads(content)
                intent = decision.get("intent", "chat")
            except Exception as e:
                intent = "chat"
            
            return {"intent_result": intent}

    def handler_music(state: State):
        user_text = state["graph_state"][-1].content
        tool_result = set_music(user_text)
        return {"graph_state": [AIMessage(content=f"J'ai lancé la musique." if tool_result else "Une erreur s'est produite lors de la lecture de la musique.")]}

    def handler_watering(state: State):
        tool_result = plant_watering()
        return {"graph_state": [AIMessage(content=f"J'ai lancé l'arrosage" if tool_result else "Une erreur s'est produite lors de l'arrosage.")]}

    def handler_chat(state: State):
        messages = [SYSTEM_PROMPT] + state["graph_state"]
        response = model.invoke(messages)
        return {"graph_state": [response]}

    def route_decision(state: State):
        return state.get("intent_result", "chat")
        
    workflow = StateGraph(State)
    workflow.add_node("router", intent_condition)
    workflow.add_node("watering", handler_watering)
    workflow.add_node("music", handler_music)
    workflow.add_node("chat", handler_chat)
    
    workflow.add_edge(START, "router")
    workflow.add_conditional_edges(
        "router",
        lambda state: route_decision(state),
        {"watering": "watering", "music": "music", "chat": "chat"},
    )
    workflow.add_edge("watering", END)
    workflow.add_edge("music", END)
    workflow.add_edge("chat", END)

    app = workflow.compile()
    return app

if __name__ == "__main__":
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../Frontend")), name="static")
    agent =  agent_factory()

    async def agent_worker(agent, websocket, message_queue):
        chat_history = []
        while True:
            try:
                user_input = await message_queue.get()
                # user_input = await websocket.receive_text()
                print (f"Received from WebSocket: {user_input}")

                inputs = {
                    "graph_state": [
                        HumanMessage(content=user_input)
                    ]
                }
                # print("--- Beginning of execution ---")

                config = {"recursive_limit": 3, "max_iterations": 2}
                conversation_state = {"graph_state": []}

                for event in agent.stream(inputs, config= config):
                    for node_name, node_output in event.items():
                        # print(f"\n[Node executed : {node_name}]")
                        # print("Output :", node_output)
                        if "graph_state" in node_output:
                            conversation_state = node_output  # Update the conversation state with the latest output
                            # Update the conversation state with the latest output
                # print("\n--- End of execution ---")

                # Get last AI response:
                if conversation_state["graph_state"]:
                        last_response = conversation_state["graph_state"][-1]
                        if isinstance(last_response, AIMessage):
                            ai_text = last_response.content

                chat_history.append(BasicInteraction(user_message=user_input, ai_message=ai_text))
                await websocket.send_json({
                    "user_message": user_input,
                    "ai_message": ai_text
                })
            except Exception as e:
                print(f"Error occurred in agent workflow: {e}")
    
    @app.get("/")
    async def get_index():
        html_path = os.path.join(os.path.dirname(__file__), "../Frontend/index.html")
        return FileResponse(html_path)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        message_queue = asyncio.Queue()
        await websocket.accept()
        print("WebSocket connection established.")

        worker_task = asyncio.create_task(agent_worker(agent, websocket, message_queue))
        try:
            while True:
                user_input = await websocket.receive_text()
                await message_queue.put(user_input)

        except WebSocketDisconnect:
            print("Client disconnected.")
            worker_task.cancel()
        except Exception as e:
            print(f"Error occurred: {e}")
            worker_task.cancel()

    uvicorn.run(app, host="127.0.0.1", port=9000)
