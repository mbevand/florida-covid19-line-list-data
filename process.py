#!/usr/bin/python3
#
# Analyzes Florida COVID-19 line list data by age bracket over time.

import sys
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import rcParams

# This CSV is found at https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data (click Download → Spreadsheet)
csv_url = "https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv"
buckets_days = 4
buckets_ages = [(0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 49), (50, 54), (55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89), (90, 199), ]
#buckets_ages = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 89), (90, 199), ]

def print_stats(cases_per_bracket, ages, df):
    print(
        f"Number of COVID-19 cases per {buckets_days}-day time period in Florida by age "
        "bracket over time:"
    )
    print(f"{'period_start':>12},", end="")
    for (low_age, high_age) in buckets_ages:
        print(f" {low_age:02d}-{high_age:02d},", end="")
    print(" median_age")
    for period in sorted(cases_per_bracket):
        print(f"{str(period):>12},", end="")
        for bucket in buckets_ages:
            print(f" {cases_per_bracket[period][bucket]:5d},", end="")
        print(f"  {np.median(ages[period]):.1f}")
    cases_total = len(df)
    cases_age_unknown = df["Age"].isnull().sum()
    print(
        f"(Last period's data may be incomplete. Age unknown for {cases_age_unknown} out of "
        f"{cases_total} cases.)"
    )

def gen_heatmap(cases_per_bracket, filename, comment, sqrt):
    rcParams["figure.titlesize"] = "x-large"
    (fig, ax) = plt.subplots(dpi=300)
    periods = sorted(cases_per_bracket.keys())
    def fmt_dates(x, pos=None):
        if 0 <= x < len(periods):
            return periods[int(x)]
    def fmt_age(x, pos=None):
        if 0 <= x < len(buckets_ages):
            (low_age, high_age) = buckets_ages[int(x)]
            return f"{low_age}-{high_age}"
    a = np.zeros((len(buckets_ages), len(periods)))
    for (j, period) in enumerate(periods):
        for (i, bracket) in enumerate(buckets_ages):
            # Square root makes the heat map brighter (by dampening the highest values).
            val = cases_per_bracket[period][bracket]
            a[i, j] = np.sqrt(val) if sqrt else val
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=15, integer=True))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_dates))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=20, integer=True))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_age))
    fig.autofmt_xdate()
    ax.set_ylabel("Age range")
    ax.tick_params(axis="x", which="both", labelsize="small")
    ax.text(
        -0.1,
        -0.2,
        f"Pixel intensity represents {comment}.\n"
        "Source: https://github.com/mbevand/florida-covid19-line-list-data\n"
        "Created by: Marc Bevand — @zorinaq",
        transform=ax.transAxes,
        verticalalignment="top",
    )
    fig.suptitle("Heatmap Of COVID-19 Cases In Florida By Age Bracket Over Time")
    ax.imshow(a, cmap="inferno", origin="lower", interpolation="nearest", aspect="auto")
    plt.savefig(f"{filename}.png", bbox_inches="tight")

def main():
    try:
        fname = sys.argv[1]
        print(f"Opening {fname}...")
        df = pd.read_csv(sys.argv[1])
    except IndexError:
        print(f"Downloading from {csv_url}...")
        df = pd.read_csv(csv_url)
    # ChartDate is the date the case was counted according the header of table
    # "Coronavirus: line list of cases" in:
    # http://ww11.doh.state.fl.us/comm/_partners/action/report_archive/state/state_reports_latest.pdf
    # The timestamp is formatted as "2020/06/28 05:00:00+00". We truncate after the whitespace
    # to ignore the time.
    df["ChartDate_parsed"] = pd.to_datetime(
            df["ChartDate"].apply(lambda x: x.split(' ')[0]), format="%Y/%m/%d"
    )
    # Pick an arbitrary point in time to align the time periods. Today's date is usually
    # the best choice assuming the CSV file contains current data (ie. data up to yesterday)
    # because this ensures the last period ends on yesterday
    reference = datetime.datetime.now().date()
    df["Delta"] = df["ChartDate_parsed"].apply(lambda date: (date.date() - reference).days)
    df["Period"] = df["Delta"].apply(
        lambda delta: reference + datetime.timedelta(days=delta - delta % buckets_days)
    )
    # cases_per_bracket[datetime.date(y, m, d)][(low_age, high_age)] is the number of
    # cases for the period of time starting on datetime.date(y, m, d) in the age bracket
    # low_age to high_age.
    cases_per_bracket = {}
    # ages[datetime.date(y, m, d)]] is the list of case ages for the period of time
    # starting on datetime.date(y, m, d).
    ages = {}
    non_null = df[~df["Age"].isnull()]
    for period in set(df["Period"]):
        cases_per_bracket[period] = {bucket: 0 for bucket in buckets_ages}
        ages[period] = []
        in_period = non_null["Period"] == period
        for bucket in buckets_ages:
            (low_age, high_age) = bucket
            in_age_bucket = (low_age <= non_null["Age"]) & (non_null["Age"] <= high_age)
            in_period_and_age = in_period & in_age_bucket
            cases_per_bracket[period][bucket] = in_period_and_age.sum()
            ages[period].extend(list(non_null[in_period_and_age]["Age"]))
    share_positive = {}
    for (period, cases_data) in cases_per_bracket.items():
        total_cases = sum(cases_data.values())
        share_positive[period] = {}
        for (bucket, cases) in cases_data.items():
            share_positive[period][bucket] = cases / total_cases
    print_stats(cases_per_bracket, ages, df)
    gen_heatmap(cases_per_bracket, "heatmap",
            f"number of cases reported per {buckets_days}-day time period", True)
    gen_heatmap(share_positive, "heatmap_age_share",
            "share of cases in the age bracket among all cases in the\n"
            f"{buckets_days}-day time period", True)

if __name__ == "__main__":
    main()
