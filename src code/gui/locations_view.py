from tkinter import *
from tkinter import ttk, messagebox
from gui.location_window import LocationWindow


class LocationsView(ttk.Treeview):
    def __init__(self, containing_frame, db_manager):
        ttk.Treeview.__init__(self, containing_frame, selectmode='browse')
        self.containing_frame = containing_frame
        self.db_manager = db_manager
        self['show'] = 'headings'
        self["columns"] = ("1", "2", "3", "4", "5", "6", "7", "8")
        self.column("#0", width=0, minwidth=0, stretch=YES)
        self.column("1", width=40, minwidth=80, stretch=YES)
        self.column("2", width=160, minwidth=80, stretch=YES)
        self.column("3", width=80, minwidth=50, stretch=YES)
        self.column("4", width=80, minwidth=50, stretch=YES)
        self.column("5", width=80, minwidth=50, stretch=YES)
        self.column("6", width=80, minwidth=50, stretch=YES)
        self.column("7", width=80, minwidth=50, stretch=YES)
        self.column("8", width=80, minwidth=50, stretch=YES)

        self.heading("1", text="ID", anchor=W)
        self.heading("2", text="Name", anchor=W)
        self.heading("3", text="Latitude", anchor=W)
        self.heading("4", text="Longitude", anchor=W)
        self.heading("5", text="Category", anchor=W)
        self.heading("6", text="Sub Category", anchor=W)
        self.heading("7", text="Country", anchor=W)
        self.heading("8", text="Rating", anchor=W)

        self.bind("<Double-1>", self.location_double_click)

        self.load_more_button = Button(self.containing_frame, text="Load 50 more", width=20, command=self.load_more)
        self.load_more_button.pack(side="bottom", pady=(15, 5))

        scrollbar = ttk.Scrollbar(self.containing_frame, orient="vertical", command=self.yview)
        scrollbar.pack(side='right', fill='y')
        self.configure(yscrollcommand=scrollbar.set)

        self.pack(expand=True, fill=BOTH)

    def load_more(self):
        results, err = self.db_manager.proceedLastSearchQuery(limit_size=50)
        if (not results):
            messagebox.showinfo("Error", err)
            return

        for result in results:
            self.insert_row(result)

    def insert_row(self, row_values):
        self.insert(parent="", index="end", iid=None, values=row_values)

    def clear_table(self):
        self.delete(*self.get_children())

    def location_double_click(self, event):
        selected = self.selection()[0]
        location = self.item(selected)["values"]
        LocationWindow(location, self.db_manager)
