from ctypes import windll
from tkinter import *

from gui.consts import WIDTH, HEIGHT, FRAME_BG
from gui.locations_view import LocationsView
from gui.login_window import LoginWindow
from gui.profile_window import ProfileWindow
from gui.registration_window import RegWindow
from gui.search_tabs_notebook import SearchTabsNotebook
from gui.statistics_window import StatisticsWindow


class MainGUI:

    def __init__(self, db_manager):
        windll.shcore.SetProcessDpiAwareness(1)  # fix blurred fonts

        self.window = Tk()
        self.window.title("Around The World")
        self.window.geometry(str(WIDTH) + 'x' + str(HEIGHT))

        self.reg_window = None
        self.login_window = None
        self.locations_view = None
        self.db_manager = db_manager

        # Create right frame
        right_frame = Frame(self.window, bg=FRAME_BG, bd=10)
        right_frame.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)
        self.create_locations_view(right_frame)

        left_frame = Frame(self.window, bg=FRAME_BG, bd=3)
        left_frame.place(relx=0, rely=0, relwidth=0.2, relheight=1)
        # Create Tab Control
        left_tabs_control = SearchTabsNotebook(left_frame, db_manager, self.locations_view, self.window)
        left_tabs_control.pack(expand=True, fill=BOTH)

        menu_widget = Menu(self.window)

        menu_widget.add_command(label="Profile", command=self.create_profile_window)
        menu_widget.add_command(label="Statistics", command=self.create_statistics_window)
        menu_widget.add_command(label="Quit", command=self.window.destroy)

        # display the menu
        self.window.config(menu=menu_widget)

    def run(self):
        self.window.mainloop()

    # windows creation

    def create_login_window(self):
        # destroy registration windows if exists
        if (self.reg_window):
            self.reg_window.destroy()
        self.login_window = LoginWindow(self, self.db_manager)

    def create_reg_window(self):
        # destroy login windows if exists
        if (self.login_window):
            self.login_window.destroy()
        self.reg_window = RegWindow(self, self.db_manager)

    def create_profile_window(self):
        if not self.db_manager.isUserLoggedIn():
            self.create_login_window()
            return
        self.profile_window = ProfileWindow(self.db_manager)

    def create_statistics_window(self):
        self.statistics_window = StatisticsWindow(self.db_manager)

    def create_locations_view(self, containing_frame):
        self.locations_view = LocationsView(containing_frame, self.db_manager)
