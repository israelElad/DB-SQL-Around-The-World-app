"""Implementation of the MyFilterList widget."""

# Python 3
from tkinter import *
from tkinter.ttk import *

__all__ = ["MyFilterList"]


class MyFilterList(Frame):
    """A combination Listbox and Entry widget with automatic filtering.
    The constructor accepts the usual Tkinter keyword arguments, plus
    a handful of its own:
      display_rule (function)
        Function returning the display text for a given item.
        See the module documentation for arguments and return types.
      filter_rule (function)
        Function returning whether the entered text matches a given item.
        See the module documentation for arguments and return types.
      source (list or other iterable)
        Values to display in the Listbox widget.
    """

    def __init__(self, master, **kw):
        Frame.__init__(self, master)

        # Source values for the Listbox widget
        self._source = []

        # Values in self._source matching self._filter_rule
        self._filtered_values = []

        # Default item display and filter rules
        self._display_rule = self.default_display_rule
        self._filter_rule = self.default_filter_rule

        # Frame for the Listbox widget
        self._list_frame = Frame(self,
                                 borderwidth=1,
                                 relief="sunken")
        self._list_frame.pack(side="bottom", expand=1, fill="both")

        # Listbox
        self._listbox = Listbox(self._list_frame,
                                takefocus=0,
                                exportselection=0,
                                borderwidth=0,
                                relief="flat")
        self._listbox.pack(side="left", expand=1, fill="both")

        # Scrollbar for the Listbox
        self._list_scrollbar = Scrollbar(self._list_frame,
                                         orient="vertical",
                                         command=self._listbox.yview)
        self._list_scrollbar.pack(side="right", fill="y")
        self._listbox.configure(yscrollcommand=self._list_scrollbar.set)

        # Text entry widget
        self._text_entry = Entry(self)
        self._text_entry.pack(side="top", fill="x", pady=(2, 0))

        # Key bindings for the text entry widget
        self._text_entry.bind("<KeyRelease>", self._key_release_cb)
        for seq in "<Up>", "<Down>", "<Prior>", "<Next>":
            self._text_entry.bind(seq, self._navigation_key_cb)
        self._text_entry.bind("<Control-Delete>", self.clear)

        # Forward the focus_set method to the Entry widget
        self.focus_set = self._text_entry.focus_set

        # Focus on the text entry when the Listbox is clicked
        self._listbox.bind("<FocusIn>",
                           lambda event=None: self._text_entry.focus_set())

        # Process remaining configuration options
        self.configure(**kw)

    def __setitem__(self, key, value):
        """Configure resources of a widget."""

        if key in self._CUSTOM_KEYS:
            # Process custom keys
            self._custom_configure(key, value)

        elif key in self._LISTBOX_KEYS:
            # Forward these to the Listbox widget
            self._listbox.configure(**{key: value})

        else:
            # Handle everything else normally
            Frame.configure(self, **{key: value})

    # ------------------------------------------------------------------------

    def set_entry_text(self, text):

        self._text_entry.delete(0, END)
        self._text_entry.insert(0, text)

    def bind(self, sequence=None, func=None, add=None):
        """Bind to this widget at event SEQUENCE a call to function FUNC."""

        widget = self._widget_to_bind(sequence)

        if widget == self:
            return Frame.bind(self, sequence, func, add)

        else:
            return widget.bind(sequence, func, add)

    def cget(self, key):
        """Return the resource value for a KEY given as string."""

        if key in self._CUSTOM_KEYS:
            return self._custom_cget(key)

        elif key in self._LISTBOX_KEYS:
            return self._listbox.cget(key)

        else:
            return Frame.cget(self, key)

    # Also override this alias for cget()
    __getitem__ = cget

    def configure(self, **kw):
        """Configure resources of a widget."""

        # Process custom keys first
        # Because self._CUSTOM_KEYS is already sorted, iterating through
        # it ensures our custom keys are processed in the correct order.
        for key in self._CUSTOM_KEYS:
            if key in kw:
                self._custom_configure(key, kw[key])
                del kw[key]

        # Process remaining arguments through our custom __setitem__()
        for key in kw:
            self[key] = kw[key]

    # Also override this alias for configure()
    config = configure

    def clear(self, event=None):
        """Clear entered text."""

        self._text_entry.delete(0, "end")
        self._filter_list("")

    def keys(self):
        """Return a list of all resource names of this widget."""

        return list(Frame.keys(self)) + list(self._CUSTOM_KEYS)

    def selection(self):
        """Return the selected item.
        If you have defined a custom display_rule, note that this will
        return the actual item, NOT its display text.
        This returns None if no items match the entered text.
        """

        items = list(map(int, self._listbox.curselection()))
        if items:
            return self._filtered_values[items[0]]

    def unbind(self, sequence, funcid=None):
        """Unbind for this widget for event SEQUENCE  the
        function identified with FUNCID."""

        widget = self._widget_to_bind(sequence)

        if widget == self:
            return Frame.unbind(self, sequence, funcid)

        else:
            return widget.unbind(sequence, funcid)

    # ------------------------------------------------------------------------

    def _custom_cget(self, key):
        """Return a custom resource value."""

        if key == "display_rule":
            return self._display_rule

        elif key == "filter_rule":
            return self._filter_rule

        elif key == "source":
            return self._source

    def _custom_configure(self, key, value):
        """Configure custom widget resources."""

        if key == "display_rule":
            self._display_rule = value

        elif key == "filter_rule":
            self._filter_rule = value

        elif key == "source":
            self._source = value
            self._filter_list()

    def _filter_list(self, text=""):
        """Set the list contents to items matching the specified text."""

        # Identify values matching self._filter_rule
        values = list(filter(lambda item, text=text:
                             self._filter_rule(item, text),
                             self._source))

        # Set the Listbox's display values
        self._set_listbox_contents(values)

        # Save the real values for self.selection
        self._filtered_values = values

    def _key_release_cb(self, event):
        """Process a KeyRelease event in the Entry widget."""

        if event.keysym == "Return":
            # Ignore the Return key
            pass

        elif (event.char
              or event.keysym == "BackSpace"
              or event.keysym == "Delete"):
            # Filter the list based on the contents of the Entry widget
            self._filter_list(self._text_entry.get())

    def _navigation_key_cb(self, event):
        """Process a keypress event for an arrow key, Page Up, or Page Down."""

        # The currently selected item in the listbox
        cs = list(map(int, self._listbox.curselection()))

        if event.keysym == "Up":
            # Select the item above in the Listbox
            if cs and cs[0] - 1 >= 0:
                self._set_listbox_selection(cs[0] - 1)

        elif event.keysym == "Down":
            # Select the item below in the Listbox
            if cs and cs[0] + 1 < self._listbox.size():
                self._set_listbox_selection(cs[0] + 1)

        elif event.keysym == "Prior":
            # Page Up; scroll the listbox up
            self._listbox.yview_scroll(-1, "pages")

        elif event.keysym == "Next":
            # Page Down; scroll the listbox down
            self._listbox.yview_scroll(1, "pages")

    def _set_listbox_contents(self, values):
        """Set the Listbox's contents to the specified values."""

        # Set display items
        self._listbox.delete(0, "end")
        for item in values:
            self._listbox.insert("end", self._display_rule(item))

        # Select the first item listed
        if values:
            self._set_listbox_selection(0)

        # Clear the text entry
        self._text_entry.configure(text="")

    def _set_listbox_selection(self, index):
        """Select the item at the specified index in the Listbox."""

        # Select the item at the specified index in the Listbox
        self._listbox.selection_clear(0, "end")
        self._listbox.selection_set(index)

        # Scroll the Listbox so the item at index is visible
        self._listbox.see(index)

    def _widget_to_bind(self, sequence):
        """Return the widget to bind to the specified sequence."""

        if ("Button" in sequence
                or "MouseWheel" in sequence):
            # Bind mouse button events to the Listbox widget
            return self._listbox

        elif ("Activate" in sequence
              or "Configure" in sequence
              or "Deactivate" in sequence
              or "Destroy" in sequence
              or "Enter" in sequence
              or "Expose" in sequence
              or "Leave" in sequence
              or "Map" in sequence
              or "Motion" in sequence
              or "Unmap" in sequence
              or "Visibility" in sequence):
            # Bind configuration events to the entire widget
            return self

        else:
            # Bind all other events to the Entry widget
            # (this includes all key press/release events)
            return self._text_entry

    # ------------------------------------------------------------------------

    @staticmethod
    def default_display_rule(item):
        """Return the string value of item."""
        return str(item)

    @staticmethod
    def default_filter_rule(item, text):
        """Return True if item starts with text (case-insensitive)."""
        return item.lower().startswith(text.lower())

    # ------------------------------------------------------------------------

    # Custom keys for the ScrolledFrame widget
    # Note: Keep "source" last so it's processed using any rules set during
    # the same configure() call.
    _CUSTOM_KEYS = "display_rule", "filter_rule", "source"

    # Keys for configure() to forward to the Listbox widget
    _LISTBOX_KEYS = "width", "height"
