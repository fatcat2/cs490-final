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

# prepare some data
df = pd.read_csv("data.csv")

for column in df.columns:
    df[str(column).strip()] = df[column]

df = df.filter(regex="[a-z]$", axis=1)
df["Judgement Amount"] = df["Judgement Amount"].fillna(0).astype("float")
df["Court Fees"] = df["Court Fees"].fillna(0).astype("float")
df["Evicted"] = df["Evicted"].astype("string").map({"True": True, "False": False}).astype("bool")
df["File date original"] = df["File date"]
df["File date"] = pd.to_datetime(df["File date"])
df["Color"] = df["Evicted"].astype("bool").map({True: "#268bd2", False: "#dc322f"})
df["Legend label"] = df["Evicted"].astype("bool").map({True: "Evicted", False: "Case dismissed"})
df["Evicted"] = df["Evicted"].astype("bool").map({True: "Yes", False: "No"})
df = df.sort_values(by="File date")
# initialize ColumnDataSource

id_range = range(len(df["Judgement Amount"].to_numpy()))

source = ColumnDataSource(dict(
    id=id_range,
    judgement=df["Judgement Amount"],
    case_number=df["Case Number"],
    date=df["File date original"],
    evicted=df["Evicted"],
    alpha=[1 for x in range(len(df["Judgement Amount"].to_numpy()))],
    color=df["Color"],
    label=df["Legend label"]

))

line_source = ColumnDataSource(dict(
    id=range(len(df["Judgement Amount"].to_numpy())),
    y=[df[df["Evicted"] == "Yes"]["Judgement Amount"].mean()]*len(df["Judgement Amount"].to_numpy())
))

# output to static HTML file
output_file("judgement.html")

BAR_TOOLTIPS = [
    ("Case Number", "@case_number"),
    ("Date", "@date"),
    ("Evicted?", "@evicted"),
    ("Judgement amount", "$@judgement{0,0.00}")
]

LINE_TOOLTIPS = [
    ("Average amount owed in the focused range", "$@y{0,0.00}")
]


# create a new plot
p = figure(
   tools="pan,box_zoom,reset,save",
   title="Judgement amount per eviction",
   x_axis_label='Evictions filed since May 1',
   y_axis_label='Judgement amount',
   plot_width=1600,
   plot_height=900,
   x_range=(0,len(df["Judgement Amount"].to_numpy())),
   y_range=(0, max(df["Judgement Amount"].to_numpy()))
)


# add some renderers
bars = p.vbar(
    x="id",
    top="judgement",
    color="color",
    alpha="alpha",
    legend_field="label",
    source=source)

line = p.line(
    x="id",
    y="y",
    color="#002b36",
    width=5,
    legend_label="Average amount of money owed.",
    source=line_source
)

bar_hover = HoverTool(
    renderers=[bars],
    tooltips=BAR_TOOLTIPS
)

line_hover = HoverTool(
    renderers=[line],
    tooltips=LINE_TOOLTIPS
)

callback = CustomJS(args=dict(source=source, line_source=line_source), code="""
    var data = source.data;
    var alpha = data['alpha']
    var judgement = data['judgement']
    var line_y = line_source.data['y']
    var avgList = []
    for (var i = 0; i < alpha.length; i++) {        
        if(i >= cb_obj.value[0] && i <= cb_obj.value[1]){
            alpha[i] = 1;
            avgList.push(judgement[i])
        }else{
            alpha[i] = 0.2;
        }
    }
    const arrSum = arr => arr.reduce((a,b) => a + b, 0)
    var avg = arrSum(avgList) / avgList.length
    for (var i = 0; i < alpha.length; i++){
        line_y[i] = avg
    }
    source.change.emit();
    line_source.change.emit();
""")

p.add_tools(bar_hover)
p.add_tools(line_hover)

p.sizing_mode = 'scale_width'
p.background_fill_color = "#fdf6e3"
p.border_fill_color = "#fdf6e3"
p.yaxis[0].formatter = NumeralTickFormatter(format="$0,0")
p.outline_line_color = None
range_slider = RangeSlider(start=0, end=max(id_range), value=(0,max(id_range)), step=1, title="Showing IDs")
range_slider.js_on_change('value', callback)
# range_slider.js_on_change("value", CustomJS(code="""
#     console.log('range_slider: value=' + this.value[0], this.toString())
# """))
range_slider.background = "#fdf6e3"

layout = Column(p, range_slider)
layout.sizing_mode = "scale_width"
# show the results
show(layout)