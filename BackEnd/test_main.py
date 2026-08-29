from unittest.mock import MagicMock
from langchain_core.messages import AIMessage, HumanMessage
import os
import sys

from main import agent_factory


def test_ask_agent_for_music():
    fake_model = MagicMock()
    # Retourne un unique AIMessage et non une liste
    fake_model.invoke.return_value = AIMessage(content='{"intent": "music" }')

    app = agent_factory(custom_model=fake_model)

    initial_state = {
        "graph_state": [HumanMessage(content="Allume la musique jazz")]
    }
    result = app.invoke(initial_state)

    assert result["intent_result"] == "music"
    messages = result["graph_state"]
    ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
    
    assert len(ai_messages) > 0
    assert "music" in ai_messages[-1].content.lower() or "musique" in ai_messages[-1].content.lower()