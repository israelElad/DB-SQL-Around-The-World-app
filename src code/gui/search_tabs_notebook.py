from tkinter import *
from tkinter import ttk, messagebox
from ttkwidgets import TickScale

from gui.consts import FRAME_BG
from gui.my_filter_list import MyFilterList


class SearchTabsNotebook(ttk.Notebook):
    def __init__(self, containing_frame, db_manager, locations_view, window):
        self.db_manager = db_manager
        self.locations_view = locations_view
        self.window = window
        ttk.Notebook.__init__(self, containing_frame)
        # Create first tab in left frame- search by feature tab
        self.country_search_tab = self.create_country_search_tab(containing_frame)
        # Create second tab in left frame- search by radius tab
        self.radius_search_tab = self.create_radius_search_tab(containing_frame)

    # Create first tab in left frame- search by country tab
    def create_country_search_tab(self, containing_frame):
        class_search_tab = Frame(containing_frame, bg=FRAME_BG, bd=3)
        self.add(class_search_tab, text='Search By Country')

        country_frame = Frame(class_search_tab, bg=FRAME_BG, bd=3)
        country_frame.pack(expand=True, fill=X)
        country_label = Label(country_frame, text="Country:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        country_list_items, err = self.db_manager.fetchCountries()
        if(country_list_items is None):
            messagebox.showinfo("Error", err)
        self.country_country_filter_list = self.create_filter_list(country_frame, country_list_items)

        f_class_frame = Frame(class_search_tab, bg=FRAME_BG, bd=3)
        f_class_frame.pack(expand=True, fill=X)
        f_class_label = Label(f_class_frame, text="Category:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        f_class_list_items, err = self.db_manager.fetchFeatureClasses()
        if(f_class_list_items is None):
            messagebox.showinfo("Error", err)
        f_class_list_items.insert(0, "")
        self.country_f_class_filter_list = self.create_country_f_class_filter_list(f_class_frame, f_class_list_items)

        self.country_f_code_frame = Frame(class_search_tab, name="country_f_code_frame", bg=FRAME_BG, bd=3)
        self.country_f_code_frame.pack(expand=True, fill=X)
        f_code_label = Label(self.country_f_code_frame, text="Sub Category:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        f_code_list_items = ["Please choose category first!"]
        self.country_f_code_filter_list = self.create_filter_list(self.country_f_code_frame, f_code_list_items)

        trip_frame = Frame(class_search_tab, bg=FRAME_BG, bd=3)
        trip_frame.pack(expand=True, fill=X)
        self.country_trip_type_val = StringVar()
        self.country_trip_season_val = StringVar()
        trip_type_options, err = self.db_manager.fetchTripTypes()
        if(trip_type_options is None):
            messagebox.showinfo("Error", err)
        trip_season_options, err = self.db_manager.fetchTripSeasons()
        if(trip_season_options is None):
            messagebox.showinfo("Error", err)
        trip_type_dropmenu = ttk.OptionMenu(trip_frame, self.country_trip_type_val, "Trip type", "All", *trip_type_options,
                                            command=lambda selection: self.country_trip_type_val.set(selection))
        trip_season_dropmenu = ttk.OptionMenu(trip_frame, self.country_trip_season_val, "Trip season", "All", *trip_season_options,
                                              command=lambda selection: self.country_trip_season_val.set(selection))
        trip_type_dropmenu.config(width=10)
        trip_season_dropmenu.config(width=10)
        trip_type_dropmenu.pack(side="left", padx=3, expand=True, fill=X)
        trip_season_dropmenu.pack(side="right", padx=3, expand=True, fill=X)
        # trip_type_dropmenu.bind("<Return>", print_something)

        self.country_submit_button = Button(class_search_tab, text="Search", width=20, command=self.search_by_country_and_update_locations)
        self.country_submit_button.pack(expand=True)

        return class_search_tab

    # Create second tab in left frame- search by radius tab
    def create_radius_search_tab(self, containing_frame):
        radius_search_tab = Frame(containing_frame, bg=FRAME_BG, bd=3)
        self.add(radius_search_tab, text='Search By Radius')

        lat_frame = Frame(radius_search_tab, bg=FRAME_BG, bd=3)
        lat_frame.pack(expand=True, fill=X)
        lat_label = Label(lat_frame, text="Latitude:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        self.radius_lat_entry = Entry(lat_frame)
        self.radius_lat_entry.pack(expand=True, fill=X)

        lon_frame = Frame(radius_search_tab, bg=FRAME_BG, bd=3)
        lon_frame.pack(expand=True, fill=X)
        lon_label = Label(lon_frame, text="Longitude:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        self.radius_lon_entry = Entry(lon_frame)
        self.radius_lon_entry.pack(expand=True, fill=X)

        radius_frame = Frame(radius_search_tab, bg=FRAME_BG, bd=3)
        radius_frame.pack(expand=True, fill=X)
        radius_label = Label(radius_frame, text="Radius:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        ttk.Style().configure('Horizontal.TScale', background=FRAME_BG)  # define a style object for the scale widget
        self.radius_radius_slider = TickScale(radius_frame, from_=0, to=100, style="Horizontal.TScale", orient=HORIZONTAL, digits=0)
        self.radius_radius_slider.pack(expand=True, fill=X)

        f_class_frame = Frame(radius_search_tab, bg=FRAME_BG, bd=3)
        f_class_frame.pack(expand=True, fill=X)
        f_class_label = Label(f_class_frame, text="Category:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        f_class_list_items, err = self.db_manager.fetchFeatureClasses()
        if(f_class_list_items is None):
            messagebox.showinfo("Error", err)
        f_class_list_items.insert(0, "")
        self.radius_f_class_filter_list = self.create_radius_f_class_filter_list(f_class_frame, f_class_list_items)

        self.radius_f_code_frame = Frame(radius_search_tab, bg=FRAME_BG, bd=3)
        self.radius_f_code_frame.pack(expand=True, fill=X)
        f_code_label = Label(self.radius_f_code_frame, text="Sub Category:", anchor=W, bg=FRAME_BG).pack(expand=True, fill=X)
        f_code_list_items = ["Please choose category first!"]
        self.radius_f_code_filter_list = self.create_filter_list(self.radius_f_code_frame, f_code_list_items)

        trip_frame = Frame(radius_search_tab, bg=FRAME_BG, bd=3)
        trip_frame.pack(expand=True, fill=X)
        self.radius_trip_type_val = StringVar()
        self.radius_trip_season_val = StringVar()
        trip_type_options, err = self.db_manager.fetchTripTypes()
        if(trip_type_options is None):
            messagebox.showinfo("Error", err)
        trip_season_options, err = self.db_manager.fetchTripSeasons()
        if(trip_season_options is None):
            messagebox.showinfo("Error", err)
        trip_type_dropmenu = ttk.OptionMenu(trip_frame, self.radius_trip_type_val, "Trip type", "All", *trip_type_options,
                                            command=lambda selection: self.radius_trip_type_val.set(selection))
        trip_season_dropmenu = ttk.OptionMenu(trip_frame, self.radius_trip_season_val, "Trip season", "All", *trip_season_options,
                                              command=lambda selection: self.radius_trip_season_val.set(selection))
        trip_type_dropmenu.config(width=10)
        trip_season_dropmenu.config(width=10)
        trip_type_dropmenu.pack(side="left", padx=3, expand=True, fill=X)
        trip_season_dropmenu.pack(side="right", padx=3, expand=True, fill=X)
        # trip_type_dropmenu.bind("<Return>", print_something)

        self.radius_f_submit_button = Button(radius_search_tab, text="Search", width=20, command=self.search_by_radius_and_update_locations)
        self.radius_f_submit_button.pack(expand=True)

        return radius_search_tab

    def create_filter_list(self, frame, source):
        filter_list = MyFilterList(frame, source=source, display_rule=lambda item: item,
                                   filter_rule=lambda item, text: text.lower() in item.lower())
        filter_list.pack(expand=True, fill=X)

        def show_result(event=None):
            item = filter_list.selection()
            if item:
                filter_list.set_entry_text(item)

        # Show the result of the calculation on Return or double-click
        filter_list.bind("<Return>", show_result)
        filter_list.bind("<Double-Button-1>", show_result)
        return filter_list

    def create_country_f_class_filter_list(self, frame, source):
        filter_list = MyFilterList(frame, source=source, display_rule=lambda item: item,
                                   filter_rule=lambda item, text: text.lower() in item.lower())
        filter_list.pack(expand=True, fill=X)

        def show_result(event=None):
            item = filter_list.selection()
            if item:
                filter_list.set_entry_text(item)
                # fill list using query for all feature codes full name that match the selected feature class
                matching_f_code_list_items, err = self.db_manager.fetchFeatureCodes(item)
                if (matching_f_code_list_items is None):
                    messagebox.showinfo("Error", err)
                matching_f_code_list_items.insert(0, "")
                self.country_f_code_filter_list.destroy()
                self.country_f_code_filter_list = self.create_filter_list(self.country_f_code_frame, matching_f_code_list_items)

        # Show the result of the calculation on Return or double-click
        filter_list.bind("<Return>", show_result)
        filter_list.bind("<Double-Button-1>", show_result)
        return filter_list

    def create_radius_f_class_filter_list(self, frame, source):
        filter_list = MyFilterList(frame, source=source, display_rule=lambda item: item,
                                   filter_rule=lambda item, text: text.lower() in item.lower())
        filter_list.pack(expand=True, fill=X)

        def show_result(event=None):
            item = filter_list.selection()
            if item:
                filter_list.set_entry_text(item)
                # fill list using query for all feature codes full name that match the selected feature class
                matching_f_code_list_items, err = self.db_manager.fetchFeatureCodes(item)
                if (matching_f_code_list_items is None):
                    messagebox.showinfo("Error", err)
                matching_f_code_list_items.insert(0, "")
                self.radius_f_code_filter_list.destroy()
                self.radius_f_code_filter_list = self.create_filter_list(self.radius_f_code_frame,
                                                                         matching_f_code_list_items)

        # Show the result of the calculation on Return or double-click
        filter_list.bind("<Return>", show_result)
        filter_list.bind("<Double-Button-1>", show_result)
        return filter_list

    def search_by_radius_and_update_locations(self):
        lat_choice = self.radius_lat_entry.get()
        lon_choice = self.radius_lon_entry.get()
        radius_choice = self.radius_radius_slider.get()
        f_class_choice = self.radius_f_class_filter_list.selection()
        f_code_choice = self.radius_f_code_filter_list.selection()
        trip_type_choice = self.radius_trip_type_val.get()
        trip_season_choice = self.radius_trip_season_val.get()
        results, err = self.db_manager.searchLocations(country_name="", fclass=f_class_choice,
                                                       fcode=f_code_choice, trip_type=trip_type_choice,
                                                       trip_season=trip_season_choice, radius=radius_choice, lat=lat_choice, lng=lon_choice,
                                                       limit_size=50)

        self.locations_view.clear_table()
        # insert all results that match the user's input:
        for result in results:
            self.locations_view.insert_row(result)

    def search_by_country_and_update_locations(self):

        country_choice = self.country_country_filter_list.selection()
        f_class_choice = self.country_f_class_filter_list.selection()
        f_code_choice = self.country_f_code_filter_list.selection()
        trip_type_choice = self.country_trip_type_val.get()
        trip_season_choice = self.country_trip_season_val.get()
        results, err = self.db_manager.searchLocations(country_name=country_choice, fclass=f_class_choice, fcode=f_code_choice,
                                                       trip_type=trip_type_choice, trip_season=trip_season_choice, radius=None, lat=None, lng=None,
                                                       limit_size=50)
        self.locations_view.clear_table()
        # insert all results that match the user's input:
        for result in results:
            self.locations_view.insert_row(result)
