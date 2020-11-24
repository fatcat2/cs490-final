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

df["Month"] = df["Period"].astype("string").map(month_map)

df["label"] = df["Year"].astype("int64") + df["Month"]

print(df)

# output to static HTML file
output_file("evictions.html")

# create a new plot
p = figure(
   tools="pan,box_zoom,reset,save",
   title="Unemployment rate from 2010 to 2020 Sep.",
   x_axis_label='Time',
   y_axis_label='Unemployment rate',
   x_axis_type="datetime",
   plot_width=1600,
   plot_height=900
)

# add some renderers
p.line(
    x=df["label"],
    y=df["unemployment"],
    width=5)


p.sizing_mode = 'scale_width'

# show the results
show(p)