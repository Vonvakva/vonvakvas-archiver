"""
EXTENSIONS WITH INTERACTIONS EXAMPLE

This file is a template (starts with "_" so it is ignored).
Copy it to create your own extension.

To test: copy this file without the "_" in the name (e.g., "my_player.py")
and reload the extensions in the GUI.
"""

# Required: name displayed in the GUI
NAME = "Example Player"

# Required: where to display ("header", "dashboard", or both)
WHERE = ["dashboard"]

# Optional: seconds between updates (default: 5)
REFRESH = 3

# Optional: defines interaction buttons
INTERACTIONS = [
    {"id": "prev", "label": "prev", "tooltip": "Previous track"},
    {"id": "play", "label": "play", "tooltip": "Play"},
    {"id": "pause", "label": "pause", "tooltip": "Pause"},
    {"id": "next", "label": "next", "tooltip": "Next track"},
]

# Internal state of the extension (optional)
_is_playing = False
_current_track = "None"


def get_value():
    """
    Required: returns the value displayed in the GUI.
    Must be fast (<100ms) - runs on the interface thread.
    Returns: (text, status) or just text
    """
    if _is_playing:
        return (f"Playing: {_current_track}", "ok")
    return ("Stopped", "muted")


def on_interaction(interaction_id: str, ext):
    """
    Optional: called when the user clicks a button.
    Receives the action ID and the current extension instance.
    Optionally returns (new_text, new_status) to update the display.
    """
    global _is_playing, _current_track

    if interaction_id == "play":
        _is_playing = True
        _current_track = "Example Track"
        return ("Playing: Example Track", "ok")

    elif interaction_id == "pause":
        _is_playing = False
        return ("Paused", "warn")

    elif interaction_id == "prev":
        return ("Previous track", "ok")

    elif interaction_id == "next":
        return ("Next track", "ok")

    return None
