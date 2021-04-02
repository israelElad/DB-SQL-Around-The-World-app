from functools import partial
from tkinter import Toplevel, Label, X, Button, W, messagebox

from gui.consts import FRAME_BG, WIDTH, HEIGHT
from gui.gui_utils import create_scrollable_frame, create_review_box


class ProfileWindow(Toplevel):
    def __init__(self, db_manager):
        Toplevel.__init__(self)
        self.title("My Profile")
        self.geometry(str(int(WIDTH / 1.75)) + 'x' + str(int(HEIGHT / 2)))

        scrollable_frame = create_scrollable_frame(self)
        reviews_label = Label(scrollable_frame, text="Reviews:", anchor=W, bg=FRAME_BG, font=("Arial", 18)).pack(
            expand=True, fill=X)

        user_reviews, err = db_manager.getCurrentUserReviews()
        if(user_reviews is None):
            messagebox.showinfo("Error", err)
            return
        for review in user_reviews:
            place_id = review[1]
            trip_season = review[4]
            review_frame = create_review_box(containing_frame=scrollable_frame, location_name=review[0],
                                             reviewer_name="Me", rating=review[2], trip_type=review[3],
                                             trip_season=trip_season, reviewer_age=None, review_text=review[6])

            def delete_handler(_delete_button, _review_frame, _place_id, _trip_season):
                isSuc, err = db_manager.deleteCurrentUserReview(_place_id, _trip_season)
                if (isSuc):
                    _review_frame.destroy()
                    _delete_button.destroy()
                else:
                    messagebox.showinfo("Error", err)

            delete_button = Button(scrollable_frame, text="Delete", width=15, bg=FRAME_BG)
            """ the variables changes values inside the loop that creates many buttons. Therefore each button will call
                the handler function with the last value that has been assigned to these variables and not the value it
                had when the button was created. The solution is using partial."""
            handler = partial(delete_handler, delete_button, review_frame, place_id, trip_season)
            delete_button.configure(command=handler)
            delete_button.pack(expand=True)
