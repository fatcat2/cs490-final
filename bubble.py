import csv
from datetime import datetime
import random
from typing import Dict
from bokeh.models import renderers, RangeSlider
from bokeh.models.callbacks import CustomJS
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.models.layouts import Column
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import sliders

from bokeh.plotting import figure, output_file, show
import numpy as np
import pandas as pd


# the last one is gonna be a bubble plot
# x dimension is probably gonna be number of cases
# y dimension might be success rate
# the bubbles are gonna be the plaintiffs
# maybe the bubble size will be the amount of money they got

# prepare some data
df = pd.read_csv("data.csv")

for column in df.columns:
    df[str(column).strip()] = df[column]

df = df.filter(regex="[a-z]$", axis=1)
df["Count"] = df["Evicted"].astype("bool").map({True: 1, False: 1})
df["Successful"] = df["Evicted"].astype("bool").map({True: 1, False: 0})

df = df.groupby("Plaintiff").sum("Judgement Amount")
df["Circle size"] = df["Judgement Amount"] / max(df["Judgement Amount"].to_numpy()) * 100
df["Success rate"] = df["Successful"]/df["Count"]
df["Plaintiff"] = df.index
df["Success label"] = df["Success rate"] * 100
# initialize ColumnDataSource

print(len(df["Plaintiff"].to_numpy()))

source = ColumnDataSource(dict(
    plaintiff=df["Plaintiff"],
    count=df["Count"],
    success_rate=df["Success rate"],
    judgement=df["Judgement Amount"],
    size=df["Circle size"],
    success_label=df["Success label"]
))

# output to static HTML file
output_file("bubble.html")

CIRCLE_TOOLTIPS = [
    ("Plaintiff", "@plaintiff"),
    ("Number of cases filed", "@count"),
    ("Success rate", "@success_label%"),
    ("Total judgement amount", "$@judgement{0,0.00}")
]

# create a new plot
p = figure(
   tools="wheel_zoom,pan,box_zoom,reset,save",
   title="Number of evictions filed and the success rate of each eviction plaintiff",
   x_axis_label='Number of evictions filed',
   y_axis_label='Eviction success rate (%)',
   plot_width=1600,
   plot_height=900,
   x_range=(0,max(df["Count"].to_numpy())+10),
   y_range=(0, 1.1)
)


# add some renderers
circles = p.circle(
    x="count",
    y="success_rate",
    size="size",
    alpha=0.5,
    source=source)

circle_hover = HoverTool(
    renderers=[circles],
    tooltips=CIRCLE_TOOLTIPS
)

p.add_tools(circle_hover)

p.sizing_mode = 'scale_width'
p.background_fill_color = "#fdf6e3"
p.border_fill_color = "#fdf6e3"
p.yaxis.formatter=NumeralTickFormatter(format="0.00%")
show(p)