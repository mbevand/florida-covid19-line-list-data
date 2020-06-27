#!/usr/bin/python3
#
# Analyzes Florida COVID-19 line list data by age bracket over time.
# Source (click Download → Spreadsheet): https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
# Direct link: https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv

import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from matplotlib import rcParams

buckets_days = 7
buckets_ages = [
    (0, 4),
    (5, 9),
    (10, 14),
    (15, 19),
    (20, 24),
    (25, 29),
    (30, 34),
    (35, 39),
    (40, 44),
    (45, 49),
    (50, 54),
    (55, 59),
    (60, 64),
    (65, 69),
    (70, 74),
    (75, 79),
    (80, 84),
    (85, 89),
    (90, 199),
]


def print_stats(cases_per_bracket, ages, df):
    print(
        f"Number of COVID-19 cases per {buckets_days}-day time period in Florida by age "
        f"bracket over time:"
    )
    print(f"{'period_start':>12}", end="")
    for (low_age, high_age) in buckets_ages:
        print(f" {low_age:02d}-{high_age:02d}", end="")

    print(" median_age")

    for period in sorted(cases_per_bracket):
        print(f"{str(period):>12}", end="")
        for bucket in buckets_ages:
            print(f" {cases_per_bracket[period][bucket]:5d}", end="")

        print(f"  {np.median(ages[period]):.1f}")

    cases_total = len(df)
    cases_age_unknown = df["Age"].isnull().sum()
    print(
        f"(Last period's data is incomplete. Age unknown for {cases_age_unknown} out of "
        f"{cases_total} cases.)"
    )


def gen_heatmap(cases_per_bracket, filename):
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

    # Exclude last period because its data is incomplete.
    periods = periods[:-1]
    a = np.zeros((len(buckets_ages), len(periods)))
    for (j, period) in enumerate(periods):
        for (i, bracket) in enumerate(buckets_ages):
            # Square root makes the heat map brighter (by dampening the highest values).
            a[i, j] = math.sqrt(cases_per_bracket[period][bracket])

    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=2))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_dates))
    ax.yaxis.set_major_locator(ticker.MultipleLocator())
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_age))

    fig.autofmt_xdate()
    ax.set_ylabel("Age range")
    ax.tick_params(axis="x", which="both", labelsize="small")
    ax.text(
        -0.1,
        -0.2,
        f"Pixel intensity represents number of cases reported per {buckets_days}-day time"
        f"period.\n"
        f"Source: https://github.com/mbevand/florida-covid19-line-list-data\n"
        f"Created by: Marc Bevand — @zorinaq",
        transform=ax.transAxes,
        verticalalignment="top",
    )
    fig.suptitle("Heatmap Of COVID-19 Cases In Florida By Age Bracket Over Time")
    ax.imshow(a, cmap="inferno", origin="lower", interpolation="nearest")
    plt.savefig(f"{filename}.png", bbox_inches="tight")


def main():
    csv_url = (
        "https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv"
    )
    df = pd.read_csv(csv_url)

    # ChartDate is the date the case was counted according the header of table
    # "Coronavirus: line list of cases" in:
    # http://ww11.doh.state.fl.us/comm/_partners/action/report_archive/state/state_reports_latest.pdf
    df["Date"] = pd.to_datetime(df["ChartDate"], format="%Y/%m/%d %H:%M:%S")
    # Arbitrary point in time to align the time periods.
    reference = datetime.date(2020, 1, 4)
    df["Delta"] = df["Date"].apply(lambda date: (date.date() - reference).days)
    df["Period"] = df["Delta"].apply(
        lambda delta: reference + datetime.timedelta(days=delta - delta % buckets_days)
    )

    # cases_per_bracket[datetime.date(y, m, d)][(80, 89)] is the number of cases for
    # the period of time starting on datetime.date(y,m,d) in the age bracket 80-89.
    cases_per_bracket = {}
    # ages[datetime.date(y, m, d)]] is the list of case ages for the period of time
    # starting on datetime.date(y, m, d).
    ages = {}
    for (index, row) in df[~df["Age"].isnull()].iterrows():
        period = row["Period"]
        if period not in cases_per_bracket:
            cases_per_bracket[period] = {bucket: 0 for bucket in buckets_ages}
            ages[period] = []

        age = row["Age"]
        for bucket in buckets_ages:
            (low_age, high_age) = bucket
            if low_age <= age <= high_age:
                cases_per_bracket[period][bucket] += 1
                break

        ages[period].append(age)

    per_positive = {}
    for (period, cases_data) in cases_per_bracket.items():
        total_cases = sum(cases_data.values())
        per_positive[period] = {}
        for (bucket, cases) in cases_data.items():
            per_positive[period][bucket] = cases / total_cases

    print_stats(cases_per_bracket, ages, df)
    gen_heatmap(cases_per_bracket, "absolute")
    gen_heatmap(per_positive, "percent_over_time")


if __name__ == "__main__":
    main()
