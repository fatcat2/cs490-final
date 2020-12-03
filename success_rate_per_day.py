import csv
from datetime import datetime, timedelta
from inspect import cleandoc
from typing import Dict
from bokeh.models.annotations import Legend
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import HoverTool

from bokeh.plotting import figure, output_file, show
import numpy as np
import pandas as pd

# prepare some data

df = pd.read_csv("data.csv")


for column in df.columns:
    df[str(column).strip()] = df[column]

cleaned_df = df.filter(regex="[a-z]$", axis=1)
cleaned_df["Judgement Amount"] = cleaned_df["Judgement Amount"].fillna(0).astype("float")
cleaned_df["Court Fees"] = cleaned_df["Court Fees"].fillna(0).astype("float")
cleaned_df["Evicted"] = cleaned_df["Evicted"].astype("string").map({"True": True, "False": False}).astype("bool")
cleaned_df["File date"] = pd.to_datetime(cleaned_df["File date"])
cleaned_df["Evicted Int"] = cleaned_df["Evicted"].astype("string").map({"True": 1, "False": 0}).astype("bool")
cleaned_df["Not evicted Int"] = cleaned_df["Evicted"].astype("string").map({"True": 0, "False": 1}).astype("bool")
cleaned_df["File date"] = cleaned_df[(cleaned_df["File date"] > '2020-05-01 07:30:00')]["File date"]

print(sum(cleaned_df["Evicted Int"].to_numpy())/(sum(cleaned_df["Evicted Int"].to_numpy()) + sum(cleaned_df["Not evicted Int"].to_numpy())))

summed_df = cleaned_df.groupby("File date").sum().to_dict()
raw_days = [key for key in summed_df.get("Evicted")]
days = [key.to_pydatetime() for key in summed_df.get("Evicted")]
str_days = [date.strftime("%m/%d/%Y") for date in days]
successful_evictions = [summed_df["Evicted"].get(key) for key in summed_df.get("Evicted")]
dismissed_evictions = [summed_df["Not evicted Int"].get(key) for key in summed_df.get("Not evicted Int")]

print(summed_df)

counted_df = cleaned_df["File date"].value_counts().to_dict()
total_evictions = [counted_df.get(day) for day in raw_days]

# initialize ColumnDataSource
# source = ColumnDataSource(dict(
#     dates=days,
#     evictions=total_evictions,
#     str_days=str_days
# ))

source = {
    "dates": days,
    "Evicted": successful_evictions,
    "Not evicted": dismissed_evictions,
    "Days": str_days
}

# output to static HTML file
output_file("success_rate.html")

TOOLTIPS = [
    ("Date", "@Days"),
    ("Successful evictions", "@Evicted"),
    ("Dismissed evictions", "@{Not evicted}"),
]
# create a new plot
p = figure(
   tools="pan,reset,save,wheel_zoom",
   title="Number of evictions per day",
   x_axis_label='Time',
   y_axis_label='Number of evictions filed',
   x_axis_type="datetime",
   plot_width=1600,
   plot_height=900,
   y_range=(0, max(total_evictions) + 10)
)



# add some renderers

eviction_bar = p.vbar_stack(
    ["Evicted", "Not evicted"],
    x="dates",
    width=timedelta(days=1),
    color=["#718dbf", "#e84d60"],
    legend_label=["Evicted", "Not evicted"],
    source=source)

eviction_hover = HoverTool(
    renderers=eviction_bar,
    tooltips=TOOLTIPS
)

p.add_tools(eviction_hover)

p.sizing_mode = 'scale_width'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.outline_line_color = None
p.background_fill_color = "#fdf6e3"
p.border_fill_color = "#fdf6e3"
# show the results
show(p)