from unittest.mock import MagicMock
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
import os
import sys

from main import agent_factory


def test_ask_agent_for_music():
  fake_model = MagicMock()
  fake_model.invoke.side_effect = [
      AIMessage(
          content="",
          tool_calls=[{
              "name": "set_music",
              "args": {"style": "jazz", "volume": "5"},
              "id": "call_12345",
              "type": "tool_call",
          }],
      ),
      AIMessage(content="C'est fait, la musique jazz est lancée !"),
  ]

  app = agent_factory(custom_model=fake_model)

  initial_state = {
      "graph_state": [HumanMessage(content="Allume la musique jazz")]
  }
  result = app.invoke(initial_state)

  messages = result["graph_state"]
  tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]

  assert len(tool_messages) > 0
  assert tool_messages[0].name == "set_music"
  assert tool_messages[0].tool_call_id == "call_12345"