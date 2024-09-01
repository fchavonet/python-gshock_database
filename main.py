#!/usr/bin/python3

"""
A simple GUI application to view G-Shock watch models by series and subseries.
"""

# Standard library imports.
import os
import sys
import threading
import tkinter as tk

from PIL import Image, ImageTk
from tkinter import Canvas, Frame

# Third-party imports.
import pandas as pd
import requests

from io import BytesIO


def update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label):
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

        # Update the status bar to display the number of subseries.
        status_left_label.config(text=f"{len(subseries)} subseries.")
        status_right_label.config(text="")


def update_models(event, df, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label):
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

            # Update the status bar to display the number of models.
            status_left_label.config(text=f"{len(models)} models.")
            status_right_label.config(text="")


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


def display_image(event, df, models_listbox, image_canvas, image_cache, image_padding, status_left_label, status_right_label):
    """
    Display the image associated with the selected model and update the status bar with the model year.
    """
    # Get the currently selected model from the models_listbox.
    model_selection = models_listbox.curselection()

    # Check if a model has been selected.
    if model_selection:
        # Retrieve the selected model from the listbox.
        selected_model = models_listbox.get(model_selection)

        # Get the URL of the image associated with the selected model.
        image_url = df[df["Watch Model"] == selected_model]["Image URL"].values[0]

        # Get the year of the selected model.
        model_year = df[df["Watch Model"] == selected_model]["Year"].values[0]

        def show_image():
            # Fetch and display the image in the canvas.
            tk_image = fetch_image(image_url, image_cache, image_canvas, image_padding)
            image_canvas.delete("all")
            image_canvas.create_image((image_canvas.winfo_width() // 2, image_canvas.winfo_height() // 2), anchor=tk.CENTER, image=tk_image)

            # Keep a reference to the image to avoid garbage collection.
            image_canvas.image = tk_image

        # Load the image in a separate thread to keep the UI responsive.
        threading.Thread(target=show_image).start()

        # Update the status bar to include the model year.
        status_right_label.config(text=f"{model_year}")


def setup_ui(root, df, selected_series_global, image_cache):
    """
    Set up the user interface and bind events.
    """
    # Define a padding for the image display.
    image_padding = 10

    # Create a main horizontal frame
    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 0), padx=10)

    # Create the series frame, label and listbox.
    series_frame = tk.Frame(main_frame)
    series_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    series_label = tk.Label(series_frame, text="Series")
    series_label.pack(side=tk.TOP)

    series_listbox = tk.Listbox(series_frame, exportselection=False)
    series_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    series_scrollbar = tk.Scrollbar(series_frame, command=series_listbox.yview)
    series_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    series_listbox.config(yscrollcommand=series_scrollbar.set)

    # Create the subseries frame, label and listbox.
    subseries_frame = tk.Frame(main_frame)
    subseries_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    subseries_label = tk.Label(subseries_frame, text="Subseries")
    subseries_label.pack(side=tk.TOP)

    subseries_listbox = tk.Listbox(subseries_frame, exportselection=False)
    subseries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    subseries_scrollbar = tk.Scrollbar(subseries_frame, command=subseries_listbox.yview)
    subseries_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    subseries_listbox.config(yscrollcommand=subseries_scrollbar.set)

    # Create the models frame, label and listbox.
    models_frame = tk.Frame(main_frame)
    models_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    models_label = tk.Label(models_frame, text="Models")
    models_label.pack(side=tk.TOP)

    models_listbox = tk.Listbox(models_frame, exportselection=False)
    models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    models_scrollbar = tk.Scrollbar(models_frame, command=models_listbox.yview)
    models_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    models_listbox.config(yscrollcommand=models_scrollbar.set)

    # Bind selection events to their respective update functions for series and subseries listboxes.
    series_listbox.bind("<<ListboxSelect>>", lambda event: update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label))
    subseries_listbox.bind("<<ListboxSelect>>", lambda event: update_models(event, df, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label))
    models_listbox.bind("<<ListboxSelect>>", lambda event: display_image(event, df, models_listbox, image_canvas, image_cache, image_padding, status_left_label, status_right_label))

    # Create the picture frame, label and canas.
    picture_frame = tk.Frame(main_frame)
    picture_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    picture_label = tk.Label(picture_frame, text="Picture")
    picture_label.pack(side=tk.TOP)

    image_frame = Frame(picture_frame, bd=1, bg="white", relief=tk.SOLID)
    image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    image_canvas = Canvas(image_frame, bg="white", highlightthickness=0)
    image_canvas.pack(fill=tk.BOTH, expand=True)

    # Create a status bar frame.
    status_frame = tk.Frame(root)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

    # Create status bar labels for left and right sides.
    status_left_label = tk.Label(status_frame, text="Select a series...", anchor=tk.W)
    status_left_label.pack(side=tk.LEFT)

    status_right_label = tk.Label(status_frame, text="", anchor=tk.E)
    status_right_label.pack(side=tk.RIGHT)

    # Populate the series listbox with unique series from the DataFrame.
    for item in df["Series"].unique():
        series_listbox.insert(tk.END, item)

    # Return the image canvas for further use.
    return image_canvas


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    """
    Main function to run the G-Shock Database Viewer application.
    """
    # Load the data from the CSV file into a pandas DataFrame.
    csv_path = resource_path("shockbase.csv")
    df = pd.read_csv(csv_path)

    # Convert the "Year" column to integers (removes .0)
    df["Year"] = df["Year"].fillna(0).astype(int)

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
