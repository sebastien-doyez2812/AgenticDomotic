import webbrowser

def set_music(style="default", volume=50):
    """
    Function to set the music volume.
    """
    print(f"Setting music {style} to {volume}%.")
    webbrowser.open(f"https://www.youtube.com/results?search_query={style}+music")
    return True