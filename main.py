#!/usr/bin/python3

"""
A simple GUI application to view G-Shock watch models by series and subseries.
"""

# Standard library imports.
import tkinter as tk

# Third-party imports.
import pandas as pd


def update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, selected_series_global):
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


def update_models(event, df, subseries_listbox, models_listbox, selected_series_global):
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


def setup_ui(root, df, selected_series_global):
    """
    Set up the user interface and bind events.
    """
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
    series_listbox.bind('<<ListboxSelect>>', lambda event: update_subseries(event, df, series_listbox, subseries_listbox, models_listbox, selected_series_global))
    subseries_listbox.bind('<<ListboxSelect>>', lambda event: update_models(event, df, subseries_listbox, models_listbox, selected_series_global))

    # Arrange the series listbox and its scrollbar in the main window with padding.
    series_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 2), pady=10)
    series_scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    # Arrange the subseries listbox and its scrollbar in the main window with padding.
    subseries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 2), pady=10)
    subseries_scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    # Arrange the models listbox and its scrollbar in the main window with padding.
    models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 2), pady=10)
    models_scrollbar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)


def main():
    """
    Main function to run the G-Shock Database application.
    """
    # Load the data from the CSV file into a pandas DataFrame.
    df = pd.read_csv("shockbase.csv")

    # Global variable to store the selected series (using a list to allow modification).
    selected_series_global = [None]

    # Initialize the main application window.
    root = tk.Tk()
    root.title("G-Shock Database")
    root.geometry("620x400")
    root.resizable(False, False)

    # Set up the user interface.
    setup_ui(root, df, selected_series_global)

    # Start the main application loop.
    root.mainloop()


# Ensure the main function is called only when the script is run directly
if __name__ == "__main__":
    main()
