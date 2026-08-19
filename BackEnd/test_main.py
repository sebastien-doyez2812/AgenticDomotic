from main import app


def test_agent_run():
  initial_state = {"graph_state": [("user", "Allume la musique jazz")]}
  result = app.invoke(initial_state)

  assert result is not None
  assert "graph_state" in result
  assert len(result["graph_state"]) > 0