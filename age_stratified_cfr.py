#!/usr/bin/python3
#
# Calculates age-stratified Case Fatality Ratios based on the Florida COVID-19 line list data.

import sys, os, math, datetime
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib import rcParams

# Florida COVID-19 line list data. CSV found at:
# https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
# (click Download → Spreadsheet)
csv_url = 'https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv'
# Calculate the CFR on these age brackets
age_brackets = ((0, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 89), (90, math.inf))
# Averaging period to calculate the raw and short-term adjusted CFR
avg_days = 7
# Averaging period to calculate the long-term adjusted CFR
avg_days_long = 4 * 7
# Start the chart on this date
first_date = datetime.date(2020, 3, 15)
# "Tableau 20" colors re-ordered so the pastel colors are at the end
t20 = [(x[0] / 255., x[1] / 255., x[2] / 255.) for x in
             [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40),
              (148, 103, 189), (140, 86, 75), (227, 119, 194), (127, 127, 127),
              (188, 189, 34), (23, 190, 207), (174, 199, 232), (255, 187, 120),
               (152, 223, 138), (255, 152, 150), (197, 176, 213), (196, 156, 148),
               (247, 182, 210), (199, 199, 199), (219, 219, 141), (158, 218, 229)]]
datadir = 'data_fdoh'
censoring_rv = None

class Counters():
    deaths = 0
    deaths_adjusted = 0
    cases = 0
    cfr_raw = None
    cfr_adjusted = None
    cfr_adjusted_long = None

def age_to_bracket(age):
    for (low, high) in age_brackets:
        if age >= low and age <= high:
            return (low, high)
    raise Exception(f'Could not find bracket for age {age}')

def censoring_factor(mean, shape, days_since_onset):
    global censoring_rv
    if censoring_rv is None:
        censoring_rv = stats.gamma(shape, scale=mean / shape)
    # To adjust for censoring, deaths will be multiplied by the inverse of
    # the CDF of the Gamma distribution of onset-to-death. For example if
    # the CDF tells us only 0.25 (25%) of deaths are expected to have occured
    # on or before a given day, we will multiply deaths by 4. Exception: on
    # day 0 we can't multiply (inverse of CDF is Infinity), so we don't adjust
    # (factor set to 1.)
    if days_since_onset == 0:
        return 1
    return 1 / censoring_rv.cdf(days_since_onset)

def calc_cfr(data, mean, shape):
    all_dates = sorted(data.keys())
    last_date = all_dates[-1]
    for date in all_dates:
        for bracket in age_brackets:
            days_since_onset = (last_date - date).days
            data[date][bracket].deaths_adjusted = \
                    data[date][bracket].deaths * censoring_factor(mean, shape, days_since_onset)
            total_deaths_raw = total_deaths_adj = total_cases = 0
            total_long_deaths = total_long_cases = 0
            assert avg_days_long >= avg_days
            for delta in range(avg_days_long):
                date2 = date - datetime.timedelta(delta)
                if date2 in data:
                    p = data[date2][bracket]
                    if delta < avg_days:
                        total_deaths_raw += p.deaths
                        total_deaths_adj += p.deaths_adjusted
                        total_cases += p.cases
                    else:
                        total_long_deaths += p.deaths_adjusted
                        total_long_cases += p.cases
            if total_cases:
                data[date][bracket].cfr_raw = 100 * total_deaths_raw / total_cases
                data[date][bracket].cfr_adjusted = 100 * total_deaths_adj / total_cases
            if total_long_cases:
                data[date][bracket].cfr_adjusted_long = 100 * total_long_deaths / total_long_cases

def print_stats(data):
    print(f'{"period":>10}', end='')
    for bracket in age_brackets:
        s = f'{bracket[0]}-{bracket[1]}'
        print(f' {s:>7}', end='')
    print('')
    for (date, counters) in sorted(data.items()):
        print(f'{str(date):10}', end='')
        for bracket in age_brackets:
            if counters[bracket].cfr_raw is None:
                print(f' {"-":>7}', end='')
            else:
                print(f' {counters[bracket].cfr_raw:6.2f}%', end='')
        print('')

def bracket2str(bracket):
    if bracket[1] == math.inf:
        return f'{bracket[0]}+'
    return f'{bracket[0]}-{bracket[1]}'

def gen_chart(data, mean, shape):
    rcParams["figure.titlesize"] = "x-large"
    (fig, ax) = plt.subplots(dpi=300, figsize=(6.0, 6.0)) # default is 6.4 × 4.8
    col_i = 0
    for bracket in reversed(age_brackets):
        dates, dates2, dates3, cfrs, cfrs2, cfrs3 = [], [], [], [], [], []
        for date, counters in sorted(data.items()):
            if date >= first_date:
                if counters[bracket].cfr_raw is not None:
                    dates.append(date)
                    cfrs.append(counters[bracket].cfr_raw)
                if counters[bracket].cfr_adjusted is not None:
                    dates2.append(date)
                    cfrs2.append(counters[bracket].cfr_adjusted)
                if counters[bracket].cfr_adjusted_long is not None:
                    dates3.append(date)
                    cfrs3.append(counters[bracket].cfr_adjusted_long)
        ax.plot(dates, cfrs, linewidth=1.0, color=t20[col_i], linestyle=':')
        ax.plot(dates2, cfrs2, linewidth=1.0, color=t20[col_i], linestyle='--')
        ax.plot(dates3, cfrs3, linewidth=1.0, color=t20[col_i], linestyle='-')
        last_day, last_cfr = dates3[-1], cfrs3[-1]
        # label the last long-term adjusted CFR
        ax.annotate(f'Age {bracket2str(bracket)}: {last_cfr:.3f}%', (last_day, last_cfr),
                xytext=(15, 0), textcoords='offset points',
                verticalalignment='center', fontsize='x-small', arrowprops={'arrowstyle':'-'},
                )
        col_i += 1
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.semilogy()
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%g%%"))
    ax.set_ylabel("Case Fatality Ratio")
    ax.set_xlim(left=first_date, right=last_day)
    ax.set_ylim(bottom=.006, top=100)
    ax.grid(True, which='both', axis='both', linewidth=0.3)
    ax.grid(True, which='minor', axis='y', linewidth=0.1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.autofmt_xdate()
    ax.tick_params(axis='x', labelsize='x-small')
    fig.suptitle('CFR of Florida COVID-19 cases\nby age bracket')
    ax.text(
        -0.1,
        -0.14,
f'Solid & dashed lines: {avg_days_long}-day & {avg_days}-day moving average of the CFR of cases ordered by date of onset of symptoms,\n'
f'adjusted for right censoring assuming onset-to-death is Gamma distributed with a mean of {mean} days and\n'
f'a shape parameter of {shape}. Dotted lines: {avg_days}-day moving average of the raw CFR not adjusted for censoring.\n'
'Source: https://github.com/mbevand/florida-covid19-line-list-data          '
'Created by: Marc Bevand — @zorinaq',
        transform=ax.transAxes, verticalalignment='top', fontsize='small',
    )
    fig.savefig('age_stratified_cfr.png', bbox_inches='tight')
    plt.close()

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
    # Date of onset is EventDate
    df['date_parsed'] = pd.to_datetime(
            # Timestamps are formatted as "2020/06/28 05:00:00+00". We truncate
            # after the whitespace to ignore the time.
            df['EventDate'].apply(lambda x: x.split(' ')[0]), format='%Y/%m/%d'
    )
    data = {}
    for _, row in df.iterrows():
        age = row['Age']
        if math.isnan(age):
            continue
        date = row['date_parsed'].date()
        died = row['Died'] == 'Yes'
        if date not in data:
            data[date] = {bracket: Counters() for bracket in age_brackets}
        b = age_to_bracket(age)
        data[date][b].deaths += 1 if died else 0
        data[date][b].cases += 1
    # Parameters of the Gamma distribution of onset-to-death, calculated by gamma.py
    mean, shape = 17.5, 1.72
    calc_cfr(data, mean, shape)
    #print_stats(data)
    gen_chart(data, mean, shape)

if __name__ == '__main__':
    main()
