import csv
from datetime import datetime
from typing import Dict
from bokeh.models.sources import ColumnDataSource

from bokeh.plotting import figure, output_file, show
import numpy as np
import pandas as pd

# prepare some data
df = pd.read_csv("data.csv")

for column in df.columns:
    df[str(column).strip()] = df[column]


print(df["File date"].value_counts())

cleaned_df = df.filter(regex="[a-z]$", axis=1)
cleaned_df["Judgement Amount"] = cleaned_df["Judgement Amount"].fillna(0).astype("float")
cleaned_df["Court Fees"] = cleaned_df["Court Fees"].fillna(0).astype("float")
cleaned_df["Evicted"] = cleaned_df["Evicted"].astype("string").map({"True": True, "False": False}).astype("bool")
cleaned_df["File date"] = pd.to_datetime(cleaned_df["File date"])

summed_df = cleaned_df.groupby("File date").sum().to_dict()
raw_days = [key for key in summed_df.get("Evicted")]
days = [key.to_pydatetime() for key in summed_df.get("Evicted")]
successful_evictions = [summed_df["Evicted"].get(key) for key in summed_df.get("Evicted")]

counted_df = cleaned_df["File date"].value_counts().to_dict()
total_evictions = [counted_df.get(day) for day in raw_days]

# initialize ColumnDataSource

source = ColumnDataSource(dict(
    dates=days,
    evictions=total_evictions
))

# output to static HTML file
output_file("log_lines.html")

# create a new plot
p = figure(
   tools="pan,box_zoom,reset,save",
   title="Number of evictions per day",
   x_axis_label='Number of Evictions Filed',
   y_axis_label='Eviction Rate',
   x_axis_type="datetime",
   plot_width=1600,
   plot_height=900
)

# add some renderers
p.line(
    x="dates",
    y="evictions",
    width=5,
    source=source)


p.sizing_mode = 'scale_width'

# show the results
show(p)