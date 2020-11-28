import csv
from datetime import datetime
from typing import Dict
from bokeh.models.sources import ColumnDataSource

from bokeh.plotting import figure, output_file, show
import numpy as np
import pandas as pd

month_map = {
    "Jan": float(1/12),
    "Feb": float(2/12),
    "Mar": float(3/12),
    "Apr": float(4/12),
    "May": float(5/12),
    "Jun": float(6/12),
    "Jul": float(7/12),
    "Aug": float(8/12),
    "Sep": float(9/12),
    "Oct": float(10/12),
    "Nov": float(11/12),
    "Dec": 1
}

# prepare some data
df = pd.read_csv("unemployment.csv")

df["DateString"] = df["Period"].astype("string") + " " + df["Year"].astype("string")

df["Month"] = df["Period"].astype("string").map(month_map)

df["label"] = df["Year"].astype("int64") + df["Month"]

# output to static HTML file
output_file("unemployment.html")

TOOLTIPS = [
    ("Date", "@labels"),
    ("Unemployment rate", "@unemployment_rate%"),
]

source = ColumnDataSource(dict(
    date=df["label"].to_numpy(),
    unemployment_rate=df["unemployment rate"].to_numpy(),
    labels=df["DateString"].to_numpy()
))

# create a new plot
p = figure(
   tools="reset,save",
   title="Unemployment rate from 2010 to 2020 Sep.",
   x_axis_label='Year',
   y_axis_label='Unemployment rate (%)',
   plot_width=1600,
   plot_height=900,
   tooltips=TOOLTIPS,
   toolbar_location="below"
)

# add some renderers
p.line(
    x="date",
    y="unemployment_rate",
    source=source,
    color="#268bd2",
    width=5)


p.sizing_mode = 'scale_width'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.outline_line_color = None
p.background_fill_color = "#fdf6e3"
p.border_fill_color = "#fdf6e3"
# show the results
show(p)