import csv
from datetime import datetime, timedelta
from inspect import cleandoc
from typing import Dict
from bokeh.models.annotations import Legend
from bokeh.models.sources import ColumnDataSource

from bokeh.plotting import figure, output_file, show
import numpy as np
import pandas as pd

# prepare some data
covid_df = pd.read_csv("covid_report.csv")
covid_df = covid_df[(covid_df["DATE"] > '2020-05-01 07:30:00') & (covid_df["DATE"] < '2020-10-01 07:30:00')]
covid_daily_df = covid_df[covid_df["COUNTY_NAME"] == "Tippecanoe"].groupby("DATE").sum("COVID_COUNT")
covid_daily_df["DAY"] = covid_daily_df.index
covid_daily_df["DAY"] = pd.to_datetime(covid_daily_df["DAY"])
covid_days = covid_daily_df["DAY"].to_numpy()

df = pd.read_csv("data.csv")


for column in df.columns:
    df[str(column).strip()] = df[column]


print(df["File date"].value_counts())

cleaned_df = df.filter(regex="[a-z]$", axis=1)
cleaned_df["Judgement Amount"] = cleaned_df["Judgement Amount"].fillna(0).astype("float")
cleaned_df["Court Fees"] = cleaned_df["Court Fees"].fillna(0).astype("float")
cleaned_df["Evicted"] = cleaned_df["Evicted"].astype("string").map({"True": True, "False": False}).astype("bool")
cleaned_df["File date"] = pd.to_datetime(cleaned_df["File date"])

cleaned_df["File date"] = cleaned_df[(cleaned_df["File date"] > '2020-05-01 07:30:00') & (cleaned_df["File date"] < '2020-10-01 07:30:00')]["File date"]

summed_df = cleaned_df.groupby("File date").sum().to_dict()
raw_days = [key for key in summed_df.get("Evicted")]
days = [key.to_pydatetime() for key in summed_df.get("Evicted")]
str_days = [date.strftime("%m/%d/%Y") for date in days]
successful_evictions = [summed_df["Evicted"].get(key) for key in summed_df.get("Evicted")]

counted_df = cleaned_df["File date"].value_counts().to_dict()
total_evictions = [counted_df.get(day) for day in raw_days]

# initialize ColumnDataSource

source = ColumnDataSource(dict(
    dates=days,
    evictions=total_evictions,
    str_days=str_days
))

covid_source = ColumnDataSource(dict(
    dates=covid_days,
    cases=covid_daily_df["COVID_COUNT"]
))

# output to static HTML file
output_file("evictions.html")

TOOLTIPS = [
    ("Date", "@str_days"),
    ("Eviction", "@evictions"),
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
   tooltips=TOOLTIPS,
   y_range=(0, max(total_evictions) + 10)
)



# add some renderers


covid_bar = p.vbar(
    x="dates",
    top="cases",
    width=timedelta(days=1),
    color="#dc322f",
    alpha=0.25,
    legend_label="Daily coronavirus cases",
    source=covid_source)

eviction_bar = p.vbar(
    x="dates",
    top="evictions",
    width=timedelta(days=1),
    color="#268bd2",
    legend_label="Daily eviction cases",
    source=source)

# p.circle(
#     x="dates",
#     y="evictions",
#     size=10,
#     source=source
# )


p.sizing_mode = 'scale_width'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.outline_line_color = None
p.background_fill_color = "#fdf6e3"
p.border_fill_color = "#fdf6e3"
# show the results
show(p)