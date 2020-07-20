#!/usr/bin/python3
#
# Analyzes Florida COVID-19 line list data by age bracket over time.

import sys
import math
import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from matplotlib import rcParams
from PIL import Image

# This CSV is found at https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data (click Download → Spreadsheet)
csv_url = "https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv"
buckets_days = 7
buckets_ages = [(0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 49), (50, 54), (55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, math.inf), ]
#buckets_ages = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 89), (90, math.inf), ]
#buckets_ages = [(i, i) for i in range(100)] + [(100,math.inf)]
datadir = 'data_fdoh'

def per_1000(bucket, n):
    # Given an age bracket and a number of residents in this age bracket,
    # return the number per 1000 residents. We use the following age
    # pyramid for Florida, from https://data.census.gov (2018, table S0101)
    pyramid_florida = {
            (0,4): 1_135_392,
            (5,9): 1_127_602,
            (10,14): 1_244_592,
            (15,19): 1_234_024,
            (20,24): 1_255_590,
            (25,29): 1_419_979,
            (30,34): 1_338_536,
            (35,39): 1_324_913,
            (40,44): 1_261_791,
            (45,49): 1_351_627,
            (50,54): 1_390_341,
            (55,59): 1_449_290,
            (60,64): 1_406_864,
            (65,69): 1_291_213,
            (70,74): 1_113_021,
            (75,79): 836_522,
            (80,84): 557_028,
            (85,math.inf): 561_000,
            }
    if bucket not in pyramid_florida:
        return 0
    return 1e3 * n / pyramid_florida[bucket]

def bracket2str(bracket):
    if bracket[1] == math.inf:
        return f'{bracket[0]}+'
    if bracket[0] != bracket[1]:
        return f'{bracket[0]:02d}-{bracket[1]:02d}'
    return f'{bracket[0]}'

def print_stats(cases_per_bracket, ages, df):
    print(
        f"Number of COVID-19 cases per {buckets_days}-day time period in Florida by age "
        "bracket over time:"
    )
    print(f"{'period_start':>12},", end="")
    for bracket in buckets_ages:
        print(f" {bracket2str(bracket)},", end="")
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

def gen_heatmap(cases_per_bracket, filename, comment='', sqrt=False, title='', cm='inferno', clabel=''):
    def conv(val):
        if sqrt:
            # Square root makes the heat map brighter (by dampening the highest values).
            return np.sqrt(val)
        else:
            return val
    rcParams["figure.titlesize"] = "x-large"
    (fig, ax) = plt.subplots(dpi=300)
    periods = sorted(cases_per_bracket.keys())
    def fmt_dates(x, pos=None):
        if 0 <= x < len(periods):
            return periods[int(x)]
    def fmt_age(x, pos=None):
        if 0 <= x < len(buckets_ages):
            return bracket2str(buckets_ages[int(x)])
    a = np.zeros((len(buckets_ages), len(periods)))
    for (j, period) in enumerate(periods):
        for (i, bracket) in enumerate(buckets_ages):
            val = cases_per_bracket[period][bracket]
            a[i, j] = conv(val)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=15, integer=True))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_dates))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=20, integer=True))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_age))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.autofmt_xdate()
    ax.set_ylabel("Age range" if buckets_ages[0][0] != buckets_ages[0][1] else "Age")
    ax.set_xlabel(f"Start date of {buckets_days}-day period")
    ax.tick_params(axis="x", which="both", labelsize="small")
    years = 1 + buckets_ages[0][1] - buckets_ages[0][0]
    ax.text(
        -0.1,
        -0.25,
        f"Each pixel represents a {buckets_days}-day time period and {years}-year age bracket.\n"
        f"Pixel intensity represents the {comment}.\n"
        "Source: https://github.com/mbevand/florida-covid19-line-list-data\n"
        "Created by: Marc Bevand — @zorinaq",
        transform=ax.transAxes,
        verticalalignment="top",
    )
    fig.suptitle(f"Heatmap Of COVID-19 Cases In Florida\nBy Age Over Time{title}")
    img = ax.imshow(a, cmap=cm, origin="lower", interpolation="nearest", aspect="auto")
    if sqrt:
        if filename == 'heatmap_per_capita':
            ticks = list(range(100)) + [0.5]
        else:
            ticks = [0, 20] + [i * 10**e for e in range(2, 5) for i in (1, 2, 5)]
        cbar = fig.colorbar(img, ticks=[conv(x) for x in ticks])
        cbar.ax.set_yticklabels(ticks)
    else:
        cbar = fig.colorbar(img)
    cbar.set_label(clabel)
    plt.savefig(f"{filename}.png", bbox_inches="tight")

def gen_gif(df):
    non_null = df[~df["Age"].isnull()]
    periods = list(set(non_null["Period"]))
    periods.sort()
    max_cases = 0
    for period in periods:
        most_cases = non_null[non_null["Period"] == period]["Age"].value_counts().max()
        max_cases = most_cases if most_cases > max_cases else max_cases
    ages = list(set(non_null["Age"].astype("int")))
    ages.sort()
    max_age = max(ages)
    images = []
    for period in periods:
        cp = sns.countplot(
            non_null[non_null["Period"] == period]["Age"].values.astype("int"),
            order=ages,
        )
        for (ind, label) in enumerate(cp.get_xticklabels()):
            if ind % 5 == 0:
                label.set_visible(True)
            else:
                label.set_visible(False)
        plt.ylim(0, max_cases)
        plt.xlim(0, max_age)
        plt.title(str(period))
        canvas = plt.get_current_fig_manager().canvas
        canvas.draw()
        pil_image = Image.frombytes(
            "RGB", canvas.get_width_height(), canvas.tostring_rgb()
        )
        plt.close("all")
        images.append(pil_image)
    images[0].save(
        "cases_ages.gif", save_all=True, append_images=images[1:], duration=350, loop=0
    )

def main():
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        try:
            files = list(filter(lambda x: x.endswith('.csv'), sorted(os.listdir(datadir))))
        except FileNotFoundError:
            files = []
        if files:
            fname = datadir + os.sep + files[-1]
        else:
            fname = csv_url
    print(f'Opening {fname}')
    df = pd.read_csv(fname)
    # We show cases by date reported (ChartDate)
    # The timestamp is formatted as "2020/06/28 05:00:00+00". We truncate
    # after the whitespace to ignore the time.
    df["date_parsed"] = pd.to_datetime(
            df["ChartDate"].apply(lambda x: x.split(' ')[0]), format="%Y/%m/%d"
    )
    # Pick a reference point in time to align the time periods. The date one day past the
    # last date in the dataset is the best choice because it aligns the last period so it
    # ends on, and includes, the last date in the dataset.
    reference = sorted(set(df['date_parsed']))[-1].date() + datetime.timedelta(days=1)
    df["Delta"] = df["date_parsed"].apply(lambda date: (date.date() - reference).days)
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
    # calculate share_positive
    share_positive = {}
    for (period, cases_data) in cases_per_bracket.items():
        total_cases = sum(cases_data.values())
        share_positive[period] = {}
        for (bucket, cases) in cases_data.items():
            share_positive[period][bucket] = 100 * cases / total_cases
    # calculate cases_per_capita
    cases_per_capita = {}
    for (period, cases_data) in cases_per_bracket.items():
        cases_per_capita[period] = {}
        for (bucket, cases) in cases_data.items():
            cases_per_capita[period][bucket] = per_1000(bucket, cases)
    # print stats and generate charts
    print_stats(cases_per_bracket, ages, df)
    gen_gif(df)
    gen_heatmap(cases_per_bracket, 'heatmap', sqrt=True, clabel='Number of cases',
            comment='number of cases reported')
    gen_heatmap(share_positive, 'heatmap_age_share', cm='viridis', clabel='Percentage of cases',
            title=' (Percentage)', comment='percentage of cases in the age bracket\namong all cases in the time period')
    gen_heatmap(cases_per_capita, 'heatmap_per_capita', sqrt=True, cm='jet', clabel='Number of cases per 1000 residents',
            title=' (Per Capita)', comment='number of cases reported per capita')

if __name__ == "__main__":
    main()
