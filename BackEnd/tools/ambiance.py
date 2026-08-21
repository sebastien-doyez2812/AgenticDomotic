from langchain_core.tools import tool

@tool
def set_music(style="default", volume=50):
    """
    Function to set the music volume.
    """
    print(f"Setting music {style} to {volume}%.")
    return True