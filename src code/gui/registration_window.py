from functools import partial
from tkinter import *
from tkinter import ttk, messagebox
import tkcalendar


class RegWindow(Toplevel):
    def __init__(self, gui, db_manager):
        Toplevel.__init__(self)
        self.title("Register")
        self.geometry("270x480")
        Label(self, text="Please enter registration details:").pack()
        Label(self, text="").pack()
        Label(self, text="Username").pack()
        username = StringVar()
        username_login_entry = Entry(self, textvariable=username)
        username_login_entry.pack()
        Label(self, text="").pack()
        Label(self, text="Email").pack()
        email = StringVar()
        email_login_entry = Entry(self, textvariable=email)
        email_login_entry.pack()
        Label(self, text="").pack()
        Label(self, text="Password").pack()
        password = StringVar()
        password__login_entry = Entry(self, textvariable=password, show='*')
        password__login_entry.pack()
        Label(self, text="").pack()

        Label(self, text="Birthday").pack()
        birthday_picker = tkcalendar.DateEntry(self, width=12, year=2000, month=1, day=1,
                                               date_pattern="dd-mm-y",
                                               background='darkblue', foreground='white', borderwidth=2)
        birthday_picker.pack()

        Label(self, text="").pack()

        validate_and_register = partial(self.validate_and_register, username.get, email.get, password.get,
                                        birthday_picker.get_date, db_manager)
        Button(self, text="Register", width=10, height=1, command=validate_and_register).pack()

        reg_labelframe = ttk.Labelframe(self, text="OR")
        reg_labelframe.pack(ipadx=20, ipady=5)
        Button(reg_labelframe, text="Log In", width=10, height=1, command=gui.create_login_window).pack()

    def validate_and_register(self, get_username, get_email, get_password, get_birthday, db_manager):
        isSuc, err = db_manager.registerUser(get_username(), get_email(), get_password(), get_birthday())
        if (isSuc):
            messagebox.showinfo("Success", "Registered and logged in successfully!")
            self.destroy()
        else:
            messagebox.showinfo("Error", err)
            self.lift()
