from tkinter import *
from tkinter import ttk, messagebox

from gui.consts import FRAME_BG, WIDTH, HEIGHT
from gui.location_window import LocationWindow


class StatisticsWindow(Toplevel):
    def __init__(self, db_manager):
        Toplevel.__init__(self)
        self.title("Statistics")
        self.geometry(str(int(WIDTH * 1.3)) + 'x' + str(int(HEIGHT / 1.3)))

        # Create top rated frame
        top_rated_frame = Frame(self, bg=FRAME_BG, bd=10)
        top_rated_frame.place(relx=0, rely=0, relwidth=0.7, relheight=1)
        top_rated_label = Label(top_rated_frame, text="20 Top rated places", anchor=W, bg=FRAME_BG, font=("Arial", 15)).pack(fill=X)
        top_rated_view=TopRatedView(top_rated_frame,db_manager)
        top_rated_results,err=db_manager.getHighestRatedLocations()
        if (top_rated_results is None):
            messagebox.showinfo("Error", err)
        for result in top_rated_results:
            top_rated_view.insert_row(result)

        # Create age frame
        avg_age_frame = Frame(self, bg=FRAME_BG, bd=10)
        avg_age_label = Label(avg_age_frame, text="Average age for each trip type and season", anchor=W, bg=FRAME_BG, font=("Arial", 15)).pack(fill=X)
        avg_age_frame.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)
        avg_age_view=AvgAgeView(avg_age_frame)
        avg_age_results,err=db_manager.getGlobalStatistics()
        if (avg_age_results is None):
            messagebox.showinfo("Error", err)
        for result in avg_age_results:
            avg_age_view.insert_row(result)


class AvgAgeView(ttk.Treeview):
    def __init__(self, containing_frame):
        ttk.Treeview.__init__(self, containing_frame, selectmode='browse')
        self['show'] = 'headings'
        self["columns"] = ("1", "2", "3")
        self.column("#0", width=0, minwidth=0, stretch=YES)
        self.column("1", width=40, minwidth=40, stretch=YES)
        self.column("2", width=40, minwidth=40, stretch=YES)
        self.column("3", width=40, minwidth=40, stretch=YES)
        self.heading("1", text="Trip season", anchor=W)
        self.heading("2", text="Trip type", anchor=W)
        self.heading("3", text="Average age", anchor=W)
        self.pack(expand=True, fill=BOTH)

    def insert_row(self, row_values):
        self.insert(parent="", index="end", iid=None, values=row_values)

    def clear_table(self):
        self.delete(*self.get_children())




class TopRatedView(ttk.Treeview):
    def __init__(self, containing_frame,db_manager):
        ttk.Treeview.__init__(self, containing_frame, selectmode='browse')
        self.db_manager=db_manager
        self['show'] = 'headings'
        self["columns"] = ("1", "2", "3", "4", "5", "6", "7", "8")
        self.column("#0", width=0, minwidth=0, stretch=YES)
        self.column("1", width=20, minwidth=20, stretch=YES)
        self.column("2", width=100, minwidth=100, stretch=YES)
        self.column("3", width=50, minwidth=50, stretch=YES)
        self.column("4", width=50, minwidth=50, stretch=YES)
        self.column("5", width=80, minwidth=80, stretch=YES)
        self.column("6", width=80, minwidth=80, stretch=YES)
        self.column("7", width=50, minwidth=50, stretch=YES)
        self.column("8", width=20, minwidth=20, stretch=YES)

        self.heading("1", text="ID", anchor=W)
        self.heading("2", text="Name", anchor=W)
        self.heading("3", text="Latitude", anchor=W)
        self.heading("4", text="Longitude", anchor=W)
        self.heading("5", text="Category", anchor=W)
        self.heading("6", text="Sub Category", anchor=W)
        self.heading("7", text="Country", anchor=W)
        self.heading("8", text="Rating", anchor=W)

        self.bind("<Double-1>", self.location_double_click)

        self.pack(expand=True, fill=BOTH)

    def insert_row(self, row_values):
        self.insert(parent="", index="end", iid=None, values=row_values)

    def clear_table(self):
        self.delete(*self.get_children())

    def location_double_click(self, event):
        selected = self.selection()[0]
        location = self.item(selected)["values"]
        LocationWindow(location, self.db_manager)
