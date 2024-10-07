import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import json

from .frame_csv import frame_csv
from .auto_category import load_categories


class Interact:
    def __init__(self, input_csv_file, output_csv_file=None):
        self.input_csv = input_csv_file
        self.output_path = output_csv_file if output_csv_file else input_csv
        self.df = frame_csv(input_csv_file)

        lookup_json_path = "data/category_lookup.json"
        self.categories = load_categories(lookup_json_path)

    def _save_changes(self):
        """Save the current dataframe to CSV."""
        self.df.to_csv(self.output_path, index=False)
        print(f"Saved changes to {self.output_path}")

    def category_editor(self):
        """Method to launch interactive category editor."""
        iter_df = self.df.copy()
        iter_df["after-change-category"] = iter_df["category"]

        def update_category(change):
            try:
                index = int(index_input.value)
            except ValueError:
                index = 0
            if index in iter_df.index:
                category_dropdown.value = iter_df.at[index, 'after-change-category']
                sorted_df = iter_df.drop(index).sort_index()
                sorted_df = pd.concat([iter_df.loc[[index]], sorted_df])
                display_dataframe(sorted_df)

        def update_after_change_category(change):
            try:
                index = int(index_input.value)
            except ValueError:
                index = 0
            if index in iter_df.index:
                new_category = category_dropdown.value
                iter_df.at[index, 'after-change-category'] = new_category
                sorted_df = iter_df.drop(index).sort_index()
                sorted_df = pd.concat([iter_df.loc[[index]], sorted_df])
                display_dataframe(sorted_df)

        def display_dataframe(df):
            clear_output(wait=True)
            display(edit_widgets)
            display(df)

        def apply_changes(b):
            """Apply changes and save to the output CSV."""
            self.df['category'] = iter_df['after-change-category']
            iter_df.drop(columns=['after-change-category'], inplace=True)
            self._save_changes()
            display_dataframe(self.df)
            self.category_editor()

        def discard_changes(b):
            nonlocal iter_df
            iter_df = self.df.copy()
            iter_df["after-change-category"] = iter_df["category"]
            display_dataframe(iter_df)

        # Create widgets
        index_input = widgets.Text(description="Index:")
        category_dropdown = widgets.Dropdown(
            options=self.categories if self.categories else self.df['category'].unique(),
            description='Category:'
        )

        apply_button = widgets.Button(description="Apply Changes")
        discard_button = widgets.Button(description="Discard Changes")

        # Set up interactions
        index_input.observe(update_category, names='value')
        category_dropdown.observe(update_after_change_category, names='value')

        apply_button.on_click(apply_changes)
        discard_button.on_click(discard_changes)

        # Widget container
        edit_widgets = widgets.VBox([index_input, category_dropdown, apply_button, discard_button])

        display_dataframe(iter_df)




