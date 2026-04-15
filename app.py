import gradio as gr #imported to create the user interface for the playlist sorting visualization
import pandas as pd #imported to handle the playlist data and display it in the UI

# PLAYLIST DATA
# This is the dataset used for the playlist.
# Each song is stored as a dictionary with attributes that will
# be used for sorting and display in the UI.

songs = [
    {"title": "What You Want", "artist": "CORTIS", "energy_score": "64", "duration": 210, "popularity": "79"},
    {"title": "GO!", "artist": "CORTIS", "energy_score": "89", "duration": 200, "popularity": "82"},
    {"title": "FaSHioN", "artist": "CORTIS", "energy_score": "100", "duration": 205, "popularity": "93"},
    {"title": "JoyRide", "artist": "CORTIS", "energy_score": "39", "duration": 203, "popularity": "74"},
    {"title": "Lullaby", "artist": "CORTIS", "energy_score": "23", "duration": 198, "popularity": "77"},
    {"title": "Mention Me", "artist": "CORTIS", "energy_score": "83", "duration": 210, "popularity": "83"},
    {"title": "Attention", "artist": "NewJeans", "energy_score": "67", "duration": 181, "popularity": "91"},
    {"title": "Hype Boy", "artist": "NewJeans", "energy_score": "90", "duration": 179, "popularity": "99"},
    {"title": "Cookie", "artist": "NewJeans", "energy_score": "45", "duration": 235, "popularity": "88"},
    {"title": "Hurt", "artist": "NewJeans", "energy_score": "16", "duration": 177, "popularity": "86"},
    {"title": "Ditto", "artist": "NewJeans", "energy_score": "37", "duration": 186, "popularity": "100"},
    {"title": "OMG", "artist": "NewJeans", "energy_score": "78", "duration": 212, "popularity": "98"},
    {"title": "Super Shy", "artist": "NewJeans", "energy_score": "71", "duration": 154, "popularity": "95"},
    {"title": "ETA", "artist": "NewJeans", "energy_score": "72", "duration": 191, "popularity": "90"},
    {"title": "Cool With You", "artist": "NewJeans", "energy_score": "54", "duration": 185, "popularity": "86"},
    {"title": "New Jeans", "artist": "NewJeans", "energy_score": "29", "duration": 109, "popularity": "87"},
    {"title": "ASAP", "artist": "NewJeans", "energy_score": "13", "duration": 155, "popularity": "84"},
    {"title": "Bubble Gum", "artist": "NewJeans", "energy_score": "63", "duration": 200, "popularity": "49"},
    {"title": "How Sweet", "artist": "NewJeans", "energy_score": "33", "duration": 199, "popularity": "85"},
    {"title": "Supernatural", "artist": "NewJeans", "energy_score": "55", "duration": 199, "popularity": "92"},
    {"title": "Saucin'", "artist": "LNGSHOT", "energy_score": "95", "duration": 205, "popularity": "79"},
    {"title": "Never Let Go", "artist": "LNGSHOT", "energy_score": "37", "duration": 210, "popularity": "73"},
    {"title": "Moonwalkin'", "artist": "LNGSHOT", "energy_score": "87", "duration": 202, "popularity": "80"},
    {"title": "Backseat", "artist": "LNGSHOT", "energy_score": "49", "duration": 198, "popularity": "69"},
    {"title": "FaceTime", "artist": "LNGSHOT", "energy_score": "75", "duration": 201, "popularity": "76"},
    {"title": "Vanilla Days", "artist": "LNGSHOT", "energy_score": "57", "duration": 204, "popularity": "67"},
]


# INPUT VALIDATION (FOR MAINTAINABILITY / EXTENSION)
def validate_song(song):
    required_keys = ["title", "artist", "energy_score", "duration", "popularity"]
    
    # Check required fields + numeric validity
    for key in required_keys:
        if key not in song:
            return False
        if key in ["energy_score", "duration", "popularity"]:
            try:
                int(song[key])
            except:
                return False
    
    return True


def validate_playlist(playlist):
    return isinstance(playlist, list) and all(validate_song(song) for song in playlist)

# LABEL MAPPING (UI FORMATTING)

# Converts internal dictionary keys into user-friendly labels
# for display in the Gradio interface.

label_map = {
    "energy_score": "Energy Score",
    "duration": "Duration",
    "popularity": "Popularity"
}

# Reverse mapping used to convert UI selection back into data keys
reverse_label_map = {v: k for k, v in label_map.items()}


# MERGE SORT (WITH FRAME TRACKING FOR ANIMATION)
def merge(left, right, sort_key, reverse, frames):
    result = []
    i = j = 0

    # Merge two sorted lists based on selected sort key
    while i < len(left) and j < len(right):
        left_val = int(left[i][sort_key])
        right_val = int(right[j][sort_key])

        # Compare values depending on sort order
        if (left_val <= right_val and not reverse) or (left_val >= right_val and reverse):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

        # Store intermediate state for UI animation
        frames.append(result + left[i:] + right[j:])

    # Append remaining items after main merge loop
    result.extend(left[i:])
    result.extend(right[j:])

    # Final state after merge step
    frames.append(result.copy())
    return result


def merge_sort(playlist, sort_key, reverse, frames):
    # Base case: list is already sorted if it has 1 or 0 elements
    if len(playlist) <= 1:
        return playlist

    # Split list into two halves
    mid = len(playlist) // 2
    left = playlist[:mid]
    right = playlist[mid:]

    # Recursively sort both halves
    left_sorted = merge_sort(left, sort_key, reverse, frames)
    right_sorted = merge_sort(right, sort_key, reverse, frames)

    # Merge sorted halves
    return merge(left_sorted, right_sorted, sort_key, reverse, frames)


# GRADIO WRAPPER (STREAMING UI OUTPUT)
def gradio_wrapper(sort_label, order):
    # Convert UI label into dataset key
    sort_key = reverse_label_map[sort_label]

    # Determine sort direction
    reverse = True if order == "Descending" else False

    frames = []

    # Run merge sort and collect intermediate steps
    merge_sort(songs.copy(), sort_key, reverse, frames)

    # Yield each frame to update UI progressively
    for frame in frames:
        df = pd.DataFrame(frame)

        # Keep only relevant columns for display
        df = df[["title", "artist", sort_key]]
        df = df.rename(columns={sort_key: label_map[sort_key]})

        # Ensure table size stays consistent (prevents UI shrinking)
        while len(df) < len(songs):
            df.loc[len(df)] = ["", "", ""]

        yield df, f"Sorting by: {sort_label} ({order})"


# GRADIO UI
with gr.Blocks(theme=gr.themes.Soft()) as app:

    gr.Markdown("# 🎵 Playlist Vibe Builder")
    gr.Markdown("Watch your playlist get sorted in real time")

    with gr.Row():

        with gr.Column(scale=1):
            sort_choice = gr.Radio(
                choices=list(label_map.values()),
                label="🎚 Sort By",
                value="Energy Score"
            )

            order_choice = gr.Radio(
                ["Ascending", "Descending"],
                label="↕ Sort Order",
                value="Ascending"
            )

            sort_btn = gr.Button("Sort Playlist 🎧")

        with gr.Column(scale=2):
            playlist_table = gr.Dataframe(label="Live Sorting 🎥🔴")
            steps_output = gr.Textbox(label="Status ⏳", lines=2)

    # Button triggers sorting animation and UI updates
    sort_btn.click(
        fn=gradio_wrapper,
        inputs=[sort_choice, order_choice],
        outputs=[playlist_table, steps_output]
    )

app.launch()
