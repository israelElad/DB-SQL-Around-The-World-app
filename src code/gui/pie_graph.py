import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PieGraph:
    def __init__(self, parent_frame, _labels, _pieSizes):
        _figure = Figure(figsize=(4.5, 4), dpi=100)
        _subplot = _figure.add_subplot(111)
        _explode = tuple(0.04 for _ in range(len(_labels)))
        _subplot.pie(_pieSizes, explode=_explode, labels=_labels, autopct='%1.1f%%', shadow=True, startangle=90, normalize=True)
        _subplot.axis('equal')
        _pie = FigureCanvasTkAgg(_figure, parent_frame)
        _pie.get_tk_widget().pack(anchor=tk.E)
