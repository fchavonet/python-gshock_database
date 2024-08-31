#!/usr/bin/python3

"""
A simple GUI application to view G-Shock watch models by series and subseries.
"""

# Standard library imports.
import tkinter as tk
import threading

from PIL import Image, ImageTk
from tkinter import Canvas, Frame

# Third-party imports.
import pandas as pd
import requests

from io import BytesIO


def update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global):
    """
    Update the subseries Listbox based on the selected series.
    """
    # Get the currently selected series from the series_listbox.
    series_selection = series_listbox.curselection()

    # Check if a series has been selected.
    if series_selection:
        # Retrieve the selected series from the listbox.
        selected_series = series_listbox.get(series_selection)

        # Store the selected series in the global list.
        selected_series_global[0] = selected_series

        # Clear the subseries listbox for new entries.
        subseries_listbox.delete(0, tk.END)

        # Get the unique subseries associated with the selected series from the DataFrame.
        subseries = df[df["Series"] == selected_series]["Subseries"].unique()

        # Populate the subseries listbox with the retrieved subseries.
        for item in subseries:
            subseries_listbox.insert(tk.END, item)

        # Clear the models listbox since a new series has been selected.
        models_listbox.delete(0, tk.END)
        
        # Clear the image canvas to remove any previously displayed image.
        image_canvas.delete("all")


def update_models(event, df, subseries_listbox, models_listbox, image_canvas, selected_series_global):
    """
    Update the models Listbox based on the selected subseries.
    """
    # Get the currently selected subseries from the subseries_listbox.
    subseries_selection = subseries_listbox.curselection()

    # Check if a subseries has been selected.
    if subseries_selection:
        # Retrieve the selected subseries from the listbox.
        selected_subseries = subseries_listbox.get(subseries_selection)

        # Check if a series has been stored globally.
        if selected_series_global[0]:
            # Use the stored series from the global list.
            selected_series = selected_series_global[0]

            # Filter the DataFrame for rows that match the selected series and subseries.
            filtered_df = df[(df["Series"] == selected_series) & (df["Subseries"] == selected_subseries)]

            # Extract the unique models from the filtered DataFrame.
            models = filtered_df["Watch Model"].unique()

            # Clear the models listbox for new entries.
            models_listbox.delete(0, tk.END)

            # Populate the models listbox with the retrieved models.
            for model in models:
                models_listbox.insert(tk.END, model)


def fetch_image(image_url, image_cache, image_canvas, image_padding):
    """
    Fetch the image from the URL asynchronously, with caching.
    """
    # Check if the image is already cached.
    if image_url in image_cache:
        return image_cache[image_url]

    # Download the image from the URL.
    response = requests.get(image_url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))

    # Get the available width and height inside the canvas.
    max_width = image_canvas.winfo_width() - 2 * image_padding
    max_height = image_canvas.winfo_height() - 2 * image_padding

    # Calculate the aspect ratio of the image.
    img_ratio = img.width / img.height

    # Determine the appropriate width and height to maintain aspect ratio.
    if img.width / max_width > img.height / max_height:
        new_width = max_width
        new_height = int(max_width / img_ratio)
    else:
        new_height = max_height
        new_width = int(max_height * img_ratio)

    # Resize the image with the new dimensions.
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert the image to a format compatible with Tkinter.
    tk_image = ImageTk.PhotoImage(img)

    # Cache the image for future use.
    image_cache[image_url] = tk_image

    # Return the Tkinter-compatible image object for display.
    return tk_image


def display_image(event, df, models_listbox, image_canvas, image_cache, image_padding):
    """
    Display the image associated with the selected model.
    """
    # Get the currently selected model from the models_listbox.
    model_selection = models_listbox.curselection()

    # Check if a model has been selected.
    if model_selection:
        # Retrieve the selected model from the listbox.
        selected_model = models_listbox.get(model_selection)

        # Get the URL of the image associated with the selected model.
        image_url = df[df["Watch Model"] == selected_model]["Image URL"].values[0]

        def show_image():
            # Fetch and display the image in the canvas.
            tk_image = fetch_image(image_url, image_cache, image_canvas, image_padding)
            image_canvas.delete("all")
            image_canvas.create_image((image_canvas.winfo_width() // 2, image_canvas.winfo_height() // 2), anchor=tk.CENTER, image=tk_image)

            # Keep a reference to the image to avoid garbage collection.
            image_canvas.image = tk_image

        # Load the image in a separate thread to keep the UI responsive.
        threading.Thread(target=show_image).start()


def setup_ui(root, df, selected_series_global, image_cache):
    """
    Set up the user interface and bind events.
    """
    # Define a padding for the image display.
    image_padding = 10

    # Create scrollbars for the series, subseries, and models listboxes.
    series_scrollbar = tk.Scrollbar(root)
    subseries_scrollbar = tk.Scrollbar(root)
    models_scrollbar = tk.Scrollbar(root)

    # Create Listboxes for series, subseries, and models, and attach the corresponding scrollbars.
    series_listbox = tk.Listbox(root, yscrollcommand=series_scrollbar.set, exportselection=False)
    subseries_listbox = tk.Listbox(root, yscrollcommand=subseries_scrollbar.set, exportselection=False)
    models_listbox = tk.Listbox(root, yscrollcommand=models_scrollbar.set, exportselection=False)

    # Configure the scrollbars to control the vertical scrolling of their respective listboxes.
    series_scrollbar.config(command=series_listbox.yview)
    subseries_scrollbar.config(command=subseries_listbox.yview)
    models_scrollbar.config(command=models_listbox.yview)

    # Populate the series listbox with unique series from the DataFrame.
    for item in df["Series"].unique():
        series_listbox.insert(tk.END, item)

    # Bind selection events to their respective update functions for series and subseries listboxes.
    series_listbox.bind("<<ListboxSelect>>", lambda event: update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global))
    subseries_listbox.bind("<<ListboxSelect>>", lambda event: update_models(event, df, subseries_listbox, models_listbox, image_canvas, selected_series_global))
    models_listbox.bind("<<ListboxSelect>>", lambda event: display_image(event, df, models_listbox, image_canvas, image_cache, image_padding))

    # Arrange the series listbox and its scrollbar in the main window with padding.
    series_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 2), pady=10)
    series_scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    # Arrange the subseries listbox and its scrollbar in the main window with padding.
    subseries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 2), pady=10)
    subseries_scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    # Arrange the models listbox and its scrollbar in the main window with padding.
    models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 2), pady=10)
    models_scrollbar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)

    # Create a frame with a border for the image display.
    image_frame = Frame(root, width=400, height=400, bd=1, bg="white", relief=tk.SOLID)
    image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 10), pady=10)

    # Create a canvas for image display with padding inside the frame.
    image_canvas = Canvas(image_frame, bg="white")
    image_canvas.pack(fill=tk.BOTH, expand=True)

    # Return the image canvas for further use.
    return image_canvas


def main():
    """
    Main function to run the G-Shock Database Viewer application.
    """
    # Load the data from the CSV file into a pandas DataFrame.
    df = pd.read_csv("shockbase.csv")

    # Global variable to store the selected series (using a list to allow modification).
    selected_series_global = [None]

    # Dictionary to cache images.
    image_cache = {}

    # Initialize the main application window.
    root = tk.Tk()
    root.title("G-Shock Database")

    # Set the size and position of the window.
    window_width = 1000
    window_height = 400
    root.geometry(f"{window_width}x{window_height}")
    root.resizable(False, False)

    # Set up the user interface.
    image_canvas = setup_ui(root, df, selected_series_global, image_cache)

    # Start the main application loop.
    root.mainloop()


# Ensure the main function is called only when the script is run directly.
if __name__ == "__main__":
    main()
