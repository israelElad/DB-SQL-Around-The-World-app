from functools import partial
from tkinter import *
from tkinter import ttk, messagebox
from gui.consts import WIDTH, HEIGHT, FRAME_BG
from gui.gui_utils import create_scrollable_frame, create_review_box
from gui.pie_graph import PieGraph


class LocationWindow(Toplevel):
    def __init__(self, location, db_manager):
        Toplevel.__init__(self)

        self.title(location[1])
        self.geometry(str(int(WIDTH / 1.04)) + 'x' + str(int(HEIGHT / 1.08)))
        self.db_manager = db_manager
        scrollable_frame = create_scrollable_frame(self)
        reviews_label = Label(scrollable_frame, text="Reviews:", anchor=W, bg=FRAME_BG, font=("Arial", 18)).pack(expand=True, fill=X)

        add_review_frame = Frame(scrollable_frame, bg='white', bd=0, highlightthickness=0)
        add_review_frame.pack(expand=True, fill=BOTH)

        # possibility to add a review
        review_text = Text(add_review_frame, bd=0, width=70, height=10, font=("Helvetica", "13"))
        review_text.pack(expand=True, fill=X)
        review_text.insert("end", ' Write your review here...')

        parameters_frame = Frame(add_review_frame, bg='white', bd=3)
        parameters_frame.pack(expand=True, fill=X)

        ttk.Style().configure('TMenubutton', background='white')  # define a style object for the scale widget
        trip_type_val = StringVar()
        trip_type_options, err = self.db_manager.fetchTripTypes()
        trip_type_dropmenu = ttk.OptionMenu(parameters_frame, trip_type_val, "Trip type", *trip_type_options)
        trip_type_dropmenu.config(width=10, style='TMenubutton')
        trip_type_dropmenu.pack(side="left", expand=True)

        trip_season_val = StringVar()
        trip_season_options, err = self.db_manager.fetchTripSeasons()
        trip_season_dropmenu = ttk.OptionMenu(parameters_frame, trip_season_val, "Trip season", *trip_season_options)
        trip_season_dropmenu.config(width=10)
        trip_season_dropmenu.pack(side="left", expand=True)

        is_anon_val = StringVar()
        is_anon_val.set(0)
        ttk.Style().configure('TCheckbutton', background='white')  # define a style object for the scale widget
        is_anon_checkbox = ttk.Checkbutton(parameters_frame, text='Anonymous', variable=is_anon_val, onvalue=1, offvalue=0 ,style='TCheckbutton')
        is_anon_checkbox.pack(side="left", expand=True)

        rating_frame = Frame(parameters_frame, bg='white', bd=3)
        rating_frame.pack(side="left", expand=True)
        rating_label = Label(rating_frame, text="Rating:", width=7, bg='white').pack(side="left")
        rating_entry = Entry(rating_frame, width=10)
        rating_entry.pack(side="left")

        sep = ttk.Separator(add_review_frame, orient=HORIZONTAL)
        sep.pack(expand=True, fill=BOTH, padx=20, pady=(5, 20), side="bottom")

        location_id = location[0]

        def add_review(location_id, rating_entry, trip_type_val, trip_season_val, is_anon_val, review_text):
            isSuc, err = db_manager.addCurrentUserReview(place_id=location_id, rating=float(rating_entry.get()), trip_type=trip_type_val.get(),
                                                         trip_season=trip_season_val.get(), anon_rew=is_anon_val.get(),
                                                         text_rew=review_text.get("1.0", END))
            if (isSuc):
                messagebox.showinfo("Success", "Review added!")
                self.destroy()
            else:
                messagebox.showinfo("Error", err)
                self.lift()

        add_review_handler = partial(add_review, location_id, rating_entry, trip_type_val, trip_season_val, is_anon_val, review_text)
        add_review_button = Button(add_review_frame, text="Add review", width=15, bg=FRAME_BG, command=add_review_handler)
        add_review_button.pack(expand=True, side="bottom", pady=10)

        location_reviews, err = db_manager.fetchLocationReviews(location_id)
        for review in location_reviews:
            trip_season = review[5]
            reviewer_name = "Anonymous" if review[6] else review[0]
            review_frame = create_review_box(containing_frame=scrollable_frame, location_name=None,
                                             reviewer_name=reviewer_name, rating=review[3], trip_type=review[4],
                                             trip_season=trip_season, reviewer_age=review[1], review_text=review[7])

        stats_frame = (ttk.Frame(self))
        stats_frame.pack(side="left", expand=False)

        trip_type_pie_label = Label(stats_frame, text=" Trip Type Statistics:", anchor=W, bg=FRAME_BG, font=("Arial", 18)).pack(
            expand=True, fill=X)
        trip_type_stats, err = db_manager.getLocationTripTypeStatistics(location_id)

        # split tuples list to labels and values
        trip_type_labels = [x[0] for x in trip_type_stats]
        trip_type_values = [x[1] for x in trip_type_stats]
        trip_type_pie = PieGraph(stats_frame, trip_type_labels, trip_type_values)

        trip_season_pie_label = Label(stats_frame, text=" Trip Season Statistics:", anchor=W, bg=FRAME_BG, font=("Arial", 18)).pack(
            expand=True, fill=X)
        trip_season_stats, err = db_manager.getLocationSeasonStatistics(location_id)
        # split tuples list to labels and values
        trip_season_labels = [x[0] for x in trip_season_stats]
        trip_season_values = [x[1] for x in trip_season_stats]
        trip_season_pie = PieGraph(stats_frame, trip_season_labels, trip_season_values)
