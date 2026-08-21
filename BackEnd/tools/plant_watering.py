from langchain_core.tools import tool

@tool
def plant_watering():
    """
    Function to simulate plant watering.
    """
    print("Watering the plants...")
    return True

