# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import csv
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.pyplot as plt
import pandas as pd

class DataFrameViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("DataFrame Viewer")

        # Create a container to hold all the frames
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}  # Dictionary to hold different frames

        self.maxsize(1000,1300)

        # Create and add frames to the dictionary
        for F in (StartPage, SecondPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the start page initially
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        # Show the requested frame and hide all others
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Welcome to your Steam library viewer!")
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Go to Second Page",
                             command=lambda: controller.show_frame("SecondPage"))
        button1.pack()

class SecondPage(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        df = pd.read_csv('steam-library.csv')
        df = df.drop(columns=['last_played'])
        df = df.iloc[:, 0:28]
        self.df = df

        label = ttk.Label(self, text="This is the Second Page")
        label.pack(pady=10, padx=10)

        self.create_dataframe_view()

        self.create_buttons()

        self.tree.pack(fill="both", expand=True)

    def create_buttons(self):
        # Frame to contain the buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        # Dictionary to keep track of sort state for each column
        sort_state = {col: tk.BooleanVar() for col in self.df.columns}

        sort_by_game_button = ttk.Button(button_frame, text="Sort by Game Name",
                                         command=lambda: self.sort_button_click('game', sort_state))
        sort_by_game_button.pack(side="left", padx=5, pady=5)

        sort_by_hours_button = ttk.Button(button_frame, text="Sort by Hours",
                                          command=lambda: self.sort_button_click('hours', sort_state))
        sort_by_hours_button.pack(side="left", padx=5, pady=5)

        sort_by_userscore_button = ttk.Button(button_frame, text="Sort by User Score",
                                              command=lambda: self.sort_button_click('userscore', sort_state))
        sort_by_userscore_button.pack(side="left", padx=5, pady=5)

        upload_button = ttk.Button(self, text="Upload CSV", command=self.upload_csv)
        upload_button.pack(pady=5)

        exportCsvButton = ttk.Button(button_frame, text="Export CSV", command=lambda: self.exportCsv(self.df))
        exportCsvButton.pack(side="left", padx=5, pady=5)

        open_window_button = ttk.Button(button_frame, text="Search", command=lambda: self.open_text_entry_window(self.df))
        open_window_button.pack(side="left", padx=5, pady=5)

    def create_dataframe_view(self):
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = tuple(self.df.columns)
        self.tree["show"] = "headings"
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        for i, row in self.df.iterrows():
            self.tree.insert("", "end", values=tuple(row))
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbarH = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        scrollbarH.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbarH.set)

    # Function to populate treeview with sorted rows
    def populate_tree_sorted(self, column, ascending=True):
        df_sorted = self.df.sort_values(by=column, ascending=ascending)
        for i, row in df_sorted.iterrows():
            self.tree.insert("", "end", values=tuple(row))

    # Function to clear existing rows from the treeview
    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def sort_button_click(self, column, sort_state):
        current_sort = sort_state.get(column)
        ascending = not current_sort.get()
        sort_state[column].set(ascending)
        self.clear_tree()
        self.populate_tree_sorted(column, ascending)

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                self.df = df  # Update the DataFrame attribute
                self.display_dataframe()  # Display the uploaded DataFrame
            except Exception as e:
                messagebox.showerror("Error", f"Error loading CSV file: {str(e)}")

    def display_dataframe(self):
        # Clear existing rows from the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Display DataFrame in the treeview
        if self.df is not None:
            self.df = self.df.drop(columns=['last_played'])
            self.df = self.df.iloc[:, 0:28]
            self.tree["columns"] = tuple(self.df.columns)
            self.tree["show"] = "headings"
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)
            for i, row in self.df.iterrows():
                self.tree.insert("", "end", values=tuple(row))
        else:
            messagebox.showwarning("Warning", "No DataFrame loaded. Please upload a CSV file.")

    def exportCsv(self, df):
        df.to_csv('out.csv', index=False)

    def open_text_entry_window(self, df):
        # Create a new window for text entry and column selection
        search_window = tk.Toplevel(self)
        search_window.title("Search")

        # Function to perform search and display results
        def search():
            search_string = entry.get()
            selected_column = column_combobox.get()

            # Check if the search string is 'nan' (case-insensitive)
            if search_string.lower() == 'nan':
                # Handle search for NaN values
                matching_rows = df[df[selected_column].isna()]
            else:
                # Check if the selected column is numeric or not
                is_numeric_column = pd.api.types.is_numeric_dtype(df[selected_column])

                # Convert search string to numeric type if applicable and the column is numeric
                if is_numeric_column:
                    try:
                        search_value = int(search_string)  # Try converting to integer
                    except ValueError:
                        try:
                            search_value = float(search_string)  # Try converting to float
                        except ValueError:
                            search_value = search_string  # Use string if conversion fails
                else:
                    search_value = search_string  # Treat as string if column is not numeric

                # Perform search on the selected column
                if is_numeric_column and isinstance(search_value, (int, float)):
                    matching_rows = df[df[selected_column] == search_value]
                else:
                    matching_rows = df[df[selected_column].astype(str) == search_value]

            # Display matching rows in a new window
            result_window = tk.Toplevel(search_window)
            result_window.title("Search Results")
            result_tree = ttk.Treeview(result_window)
            result_window.geometry("600x400")

            # Configure treeview headings
            result_tree["columns"] = tuple(matching_rows.columns)
            result_tree["show"] = "headings"
            for col in result_tree["columns"]:
                result_tree.heading(col, text=col)
                result_tree.column(col, width=100)

            # Insert matching rows into the treeview
            for i, row in matching_rows.iterrows():
                result_tree.insert("", "end", values=tuple(row))

            # Add scrollbar to the treeview
            scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=result_tree.yview)
            scrollbar.pack(side="right", fill="y")
            result_tree.configure(yscrollcommand=scrollbar.set)

            scrollbar_x = ttk.Scrollbar(result_window, orient="horizontal", command=result_tree.xview)
            scrollbar_x.pack(side="bottom", fill="x")
            result_tree.configure(xscrollcommand=scrollbar_x.set)

            result_tree.pack(fill="both", expand=True)

        # Preprocess column names to remove apostrophes and commas
        column_names = [col.replace("'", "").replace(",", "") for col in df.columns]

        # Create widgets for text entry and column selection
        ttk.Label(search_window, text="Enter Search String:").pack()
        entry = ttk.Entry(search_window)
        entry.pack()

        ttk.Label(search_window, text="Select Column:").pack()
        column_combobox = ttk.Combobox(search_window, values=column_names)
        column_combobox.pack()

        search_button = ttk.Button(search_window, text="Search", command=search)
        search_button.pack()


if __name__ == "__main__":
    app = DataFrameViewer()
    app.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
