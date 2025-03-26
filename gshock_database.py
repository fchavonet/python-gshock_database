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
from tkinter import Canvas, Frame, ttk

# Third-party imports.
import pandas as pd
import requests

from io import BytesIO


def apply_filters(df, date_filter, search_var):
    """
    Apply the date filter and the search filter to the DataFrame.
    """

    # Apply the date filter.
    if date_filter.get() == "Years":
        filtered_df = df
    elif date_filter.get() == "No date":
        filtered_df = df[df["Year"] == 0]
    else:
        filtered_df = df[df["Year"] == int(date_filter.get())]

    # Apply the search filter if the search field is not empty or equal to default text.
    search_text = search_var.get().strip()
    if search_text != "" and search_text != "Search...":
        filtered_df = filtered_df[
            filtered_df["Series"].str.contains(search_text, case=False) |
            filtered_df["Subseries"].str.contains(search_text, case=False) |
            filtered_df["Watch Model"].str.contains(search_text, case=False)
        ]
    return filtered_df


def update_series(df, series_listbox, selected_series_global, date_filter, search_var):
    """
    Update the series Listbox based on the selected date and search filter.
    """

    # Clear the series listbox.
    series_listbox.delete(0, tk.END)

    # Apply filters.
    filtered_df = apply_filters(df, date_filter, search_var)

    # Get unique series from the filtered DataFrame.
    series_list = filtered_df["Series"].unique()

    for series in sorted(series_list):
        series_listbox.insert(tk.END, series)

    # If the previously selected series is no longer available, clear it.
    if selected_series_global[0] not in series_list:
        selected_series_global[0] = None


def update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var):
    """
    Update the subseries Listbox based on the selected series, date and search filter.
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

        # Filter the DataFrame by the selected series.
        filtered_df = df[df["Series"] == selected_series]

        # Apply the date filter.
        if date_filter.get() != "Years":
            if date_filter.get() == "No date":
                filtered_df = filtered_df[filtered_df["Year"] == 0]
            else:
                filtered_df = filtered_df[filtered_df["Year"] == int(date_filter.get())]

        # Apply the search filter.
        search_text = search_var.get().strip()
        if search_text != "" and search_text != "Search...":
            filtered_df = filtered_df[
                filtered_df["Series"].str.contains(search_text, case=False) |
                filtered_df["Subseries"].str.contains(search_text, case=False) |
                filtered_df["Watch Model"].str.contains(search_text, case=False)
            ]

        # Get the unique subseries associated with the selected series.
        subseries = filtered_df["Subseries"].unique()

        # Populate the subseries listbox with the retrieved subseries.
        for item in subseries:
            subseries_listbox.insert(tk.END, item)

        # Clear the models listbox since a new series has been selected.
        models_listbox.delete(0, tk.END)

        # Clear the image canvas to remove any previously displayed image.
        image_canvas.delete("all")

        # Update the status bar to display the number of subseries.
        status_left_label.config(text=f"{len(subseries)} subseries")
        status_right_label.config(text="")


def update_models(event, df, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var):
    """
    Update the models Listbox based on the selected subseries, date and search filter.
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

            # Apply the date filter.
            if date_filter.get() != "Years":
                if date_filter.get() == "No date":
                    filtered_df = filtered_df[filtered_df["Year"] == 0]
                else:
                    filtered_df = filtered_df[filtered_df["Year"] == int(date_filter.get())]

            # Apply the search filter.
            search_text = search_var.get().strip()
            if search_text != "" and search_text != "Search...":
                filtered_df = filtered_df[
                    filtered_df["Series"].str.contains(search_text, case=False) |
                    filtered_df["Subseries"].str.contains(search_text, case=False) |
                    filtered_df["Watch Model"].str.contains(search_text, case=False)
                ]

            # Extract the unique models from the filtered DataFrame.
            models = filtered_df["Watch Model"].unique()

            # Clear the models listbox for new entries.
            models_listbox.delete(0, tk.END)

            # Populate the models listbox with the retrieved models.
            for model in models:
                models_listbox.insert(tk.END, model)

            # Update the status bar to display the number of models.
            status_left_label.config(text=f"{len(models)} models")
            status_right_label.config(text="")


def update_by_filters(df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var):
    """
    Update the series, subseries and models lists when the date or search filter is changed.
    """

    update_series(df, series_listbox, selected_series_global,date_filter, search_var)

    # If a series is selected, update subseries and models.
    if series_listbox.curselection():
        update_subseries(None, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var)
        if subseries_listbox.curselection():
            update_models(None, df, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var)
    else:
        # If no series is selected, clear subseries, models and image.
        subseries_listbox.delete(0, tk.END)
        models_listbox.delete(0, tk.END)
        image_canvas.delete("all")
        status_left_label.config(text="0 subseries")
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
            """
            """

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

    # Create a container frame to hold the top bar and the main columns.
    container = tk.Frame(root)
    container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))

    # Top bar for date selection and search.
    top_bar = tk.Frame(container)
    top_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

    # Prepare the list of dates.
    dates = sorted(df["Year"].unique())
    numeric_dates = []
    for d in dates:
        if d != 0:
            numeric_dates.append(d)
    if 0 in dates:
        dates_options = ["Years"]
        for d in numeric_dates:
            dates_options.append(str(d))
        dates_options.append("No date")
    else:
        dates_options = ["Years"]
        for d in numeric_dates:
            dates_options.append(str(d))

    # Variable for the date filter.
    date_filter = tk.StringVar()
    date_filter.set("Years")

    # Variable for the search field.
    search_var = tk.StringVar()
    search_var.set("Search...")

    def on_date_change(_):
        """
        Update the UI when the selected date changes.
        """

        update_by_filters(df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var)

    # Create and pack the date selection OptionMenu.
    date_menu = tk.OptionMenu(top_bar, date_filter, *dates_options, command=on_date_change)
    date_menu.pack(side=tk.LEFT, padx=(0, 0))

    # Create the search Entry.
    search_entry = tk.Entry(top_bar, textvariable=search_var, width=33)
    search_entry.pack(side=tk.RIGHT, padx=(0, 0))

    # Add placeholder behavior: clear on focus in and restore default text on focus out.
    def on_entry_focus_in(event):
        if search_var.get() == "Search...":
            search_var.set("")

    def on_entry_focus_out(event):
        if search_var.get().strip() == "":
            search_var.set("Search...")

    search_entry.bind("<FocusIn>", on_entry_focus_in)
    search_entry.bind("<FocusOut>", on_entry_focus_out)

    def auto_select_exact_match():
        """
        Function to auto-select exact match
        """

        search_text = search_var.get().strip()
        if search_text != "" and search_text != "Search...":
            exact_df = df[df["Watch Model"].str.lower() == search_text.lower()]

            if len(exact_df) == 1:
                row = exact_df.iloc[0]
                target_series = row["Series"]
                target_subseries = row["Subseries"]
                target_model = row["Watch Model"]

                # Select the series.
                series_items = series_listbox.get(0, tk.END)

                if target_series in series_items:
                    series_index = series_items.index(target_series)
                    series_listbox.selection_clear(0, tk.END)
                    series_listbox.selection_set(series_index)
                    series_listbox.activate(series_index)
                    selected_series_global[0] = target_series
                    update_subseries(None, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var)

                    # Select the subseries.
                    subseries_items = subseries_listbox.get(0, tk.END)

                    if target_subseries in subseries_items:
                        subseries_index = subseries_items.index(
                            target_subseries)
                        subseries_listbox.selection_clear(0, tk.END)
                        subseries_listbox.selection_set(subseries_index)
                        subseries_listbox.activate(subseries_index)
                        update_models(None, df, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var)

                        # Select the model.
                        model_items = models_listbox.get(0, tk.END)

                        if target_model in model_items:
                            model_index = model_items.index(target_model)
                            models_listbox.selection_clear(0, tk.END)
                            models_listbox.selection_set(model_index)
                            models_listbox.activate(model_index)
                            display_image(None, df, models_listbox, image_canvas, image_cache, image_padding, status_left_label, status_right_label)

    def on_search(event):
        """
        Bind the Enter key to trigger the search and auto-select if exact match.
        """

        update_by_filters(df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var)
        auto_select_exact_match()

    search_entry.bind("<Return>", on_search)

    # Placeholder for a possible element on the left.
    placeholder = tk.Label(top_bar, text="")
    placeholder.pack(side=tk.LEFT)

    # Main frame for the columns.
    main_frame = tk.Frame(container)
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 0))

    # Create the series frame, label and listbox.
    series_frame = tk.Frame(main_frame)
    series_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    series_label = tk.Label(series_frame, text="Series")
    series_label.pack(side=tk.TOP)

    series_listbox = tk.Listbox(series_frame, exportselection=False)
    series_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    series_scrollbar = ttk.Scrollbar(series_frame, orient="vertical", command=series_listbox.yview)
    series_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    series_listbox.config(yscrollcommand=series_scrollbar.set)

    # Create the subseries frame, label and listbox.
    subseries_frame = tk.Frame(main_frame)
    subseries_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    subseries_label = tk.Label(subseries_frame, text="Subseries")
    subseries_label.pack(side=tk.TOP)

    subseries_listbox = tk.Listbox(subseries_frame, exportselection=False)
    subseries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    subseries_scrollbar = ttk.Scrollbar(subseries_frame, orient="vertical", command=subseries_listbox.yview)
    subseries_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    subseries_listbox.config(yscrollcommand=subseries_scrollbar.set)

    # Create the models frame, label and listbox.
    models_frame = tk.Frame(main_frame)
    models_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    models_label = tk.Label(models_frame, text="Models")
    models_label.pack(side=tk.TOP)

    models_listbox = tk.Listbox(models_frame, exportselection=False)
    models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    models_scrollbar = ttk.Scrollbar(models_frame, orient="vertical", command=models_listbox.yview)
    models_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    models_listbox.config(yscrollcommand=models_scrollbar.set)

    # Create the picture frame, label and canvas.
    picture_frame = tk.Frame(main_frame)
    picture_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    picture_label = tk.Label(picture_frame, text="Picture")
    picture_label.pack(side=tk.TOP)

    image_frame = Frame(picture_frame, bd=1, bg="white", relief=tk.SOLID)
    image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    image_canvas = tk.Canvas(image_frame, bg="white", highlightthickness=0)

    image_canvas.pack(fill=tk.BOTH, expand=True)

    # Create a status bar frame.
    status_frame = tk.Frame(root)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

    status_left_label = tk.Label(status_frame, text="Select a series...", anchor=tk.W)
    status_left_label.pack(side=tk.LEFT)

    status_right_label = tk.Label(status_frame, text="", anchor=tk.E)
    status_right_label.pack(side=tk.RIGHT)

    # Bind selection events to their respective update functions, including the filters.
    series_listbox.bind("<<ListboxSelect>>", lambda event: update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var))
    subseries_listbox.bind("<<ListboxSelect>>", lambda event: update_models(event, df, subseries_listbox, models_listbox, image_canvas, selected_series_global, status_left_label, status_right_label, date_filter, search_var))
    models_listbox.bind("<<ListboxSelect>>", lambda event: display_image(event, df, models_listbox, image_canvas, image_cache, image_padding, status_left_label, status_right_label))

    # Populate the series listbox initially using update_series.
    update_series(df, series_listbox, selected_series_global, date_filter, search_var)

    return image_canvas


def resource_path(relative_path):
    """
    Get the absolute path to the resource, works for PyInstaller
    """

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS.
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
    window_height = 500
    root.geometry(f"{window_width}x{window_height}")
    root.resizable(False, False)

    # Set up the user interface.
    image_canvas = setup_ui(root, df, selected_series_global, image_cache)

    # Start the main application loop.
    root.mainloop()


# Ensure the main function is called only when the script is run directly.
if __name__ == "__main__":
    main()
