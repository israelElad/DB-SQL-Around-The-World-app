from tkinter import *

from gui.consts import FRAME_BG


def create_scrollable_frame(containing_frame):
    # Combining canvas with a frame makes the frame scrollable. allows to scroll through all widgets inside the frame.
    canvas = Canvas(containing_frame, borderwidth=0)
    scrollable_frame = Frame(canvas)
    scrollable_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    scrollbar = Scrollbar(containing_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="right", fill="both", expand=True)
    canvas.create_window((4, 4), window=scrollable_frame, anchor="nw")

    def onFrameConfigure(canvas):
        # Reset the scroll region to encompass the inner frame
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)
    return scrollable_frame


def create_review_box(containing_frame, location_name, reviewer_name, rating, trip_type, trip_season, reviewer_age, review_text):
    frame = Frame(containing_frame, bg='white', bd=0, highlightthickness=0)
    frame.pack(expand=True, fill=BOTH)

    canvas = Canvas(frame, bg=FRAME_BG, width=50, height=50)
    canvas.create_text(8, 4, anchor=NW, fill="darkblue", font="Times 30 italic bold", text=reviewer_name[0])
    canvas.pack(side=LEFT, anchor=NW)
    text = Text(frame, bd=0, width=70)
    text.pack(side=LEFT, anchor=NW)

    text.tag_configure("sender", font="Arial 15 bold")
    text.tag_configure("age", font="Arial 10")
    text.tag_configure("on", font="Arial 15")
    text.tag_configure("trip_type", font="Arial 10")
    text.tag_configure("trip_season", font="Arial 10")
    text.tag_configure("rating", font="Arial 15")
    text.tag_configure("message", font=("Helvetica", "13"), lmargin1=10, lmargin2=10)

    text.insert("end", reviewer_name.title(), "sender")
    if reviewer_age:
        text.insert("end", ' ('+str(reviewer_age)+' y/o)', 'age')
    if location_name:
        text.insert("end", " on ", "on")
        text.insert("end", location_name , "sender")
    text.insert("end", '\n')
    text.insert("end", "Rating: "+str(rating) + '\n', 'rating')
    text.insert("end", trip_type + ', ', 'trip_type')
    text.insert("end", trip_season + '\n', 'trip_season')
    text.insert("end", '\n')
    text.insert("end", review_text + '\n', 'message')
    return frame
