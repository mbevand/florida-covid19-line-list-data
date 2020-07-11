#!/usr/bin/python3
#
# Fit onset-to-death times in a Gamma distribution

import sys, datetime, os
import numpy as np
import scipy.stats as stats
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

debug = False

def parse_date(s, fmt='%Y-%m-%d'):
    return datetime.datetime.strptime(s, fmt).date()

def parse(fname):
    print(f'Parsing {fname}')
    # Bucketize deaths by the characteristics of their patients (age, gender, county...)
    counters = {}
    df = pd.read_csv(fname)
    for _, row in df.iterrows():
        if row['Died'] != 'Yes':
            continue
        characteristics = (
                row['County'],
                row['Age'],
                row['Gender'],
                row['Jurisdiction'],
                # Dates are sometimes formatted with a timezone ("2020/04/21 05:00:00+00"),
                # sometimes not ("2020/04/21 05:00:00"), so strip it for consistency
                row['ChartDate'].split('+')[0], # Date the case was counted
                row['EventDate'].split('+')[0], # Date of onset
                # EventDate MUST be last because calc_o2d() accesses it at a fixed index
                )
        if characteristics not in counters:
            counters[characteristics] = 0
        counters[characteristics] += 1
    if debug:
        # This printout shows that most deaths can be uniquely identified
        # with their characteristics (ie. most bucket counters are 1)
        for counter in range(1, 51):
            n = len(list(filter(lambda x: x == counter, counters.values())))
            print(f'{n} rows have characteristics seen {counter} times')
    return counters

def calc_o2d(fname, characteristics):
    # Filename must start with "YYYY-MM-DD" which represents the date the
    # FDOH line list was downloaded, and contains data for the day before
    death_reported = parse_date(os.path.basename(fname)[:10]) - datetime.timedelta(days=1)
    # Parse EventDate (last element of the characteristics tuple)
    onset = parse_date(characteristics[-1][:10], fmt='%Y/%m/%d')
    # Calculate onset-to-death
    o2d = (death_reported - onset).days
    assert o2d >= 0
    return o2d

def gen_chart(o2d, shape, loc, scale):
    fig, ax = plt.subplots(dpi=300)
    y, _ = np.histogram(o2d, bins=max(o2d) - min(o2d) + 1)
    x = range(min(o2d), max(o2d) + 1)
    ax.bar(x, y, color=(31 / 255., 119 / 255., 180 / 255., .5))
    rv = stats.gamma(shape, loc, scale)
    right = max(o2d) + 1
    x = np.linspace(0, right, 1000)
    y = rv.pdf(x) * len(o2d)
    ax.plot(x, y, color=(0, 0, 0, .7))
    ax.set_xlabel('Time from onset of symptoms to death (days)')
    ax.set_ylabel('Number of deaths')
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=10))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.set_xlim(left=-1, right=right)
    fig.suptitle(f'Onset-to-death distribution of Florida COVID-19 deaths\n(N = {len(o2d)})')
    ax.text(.5, .5, f'Gamma parameters:\nmean = {shape * scale:.1f} days\nshape = {shape:.2f}',
            transform=ax.transAxes)
    ax.text(
        -0.08, -0.15,
        'Source: https://github.com/mbevand/florida-covid19-line-list-data          '
        'Created by: Marc Bevand — @zorinaq',
        transform=ax.transAxes, fontsize='x-small', verticalalignment='top',
    )
    fig.savefig('gamma.png', bbox_inches='tight')

def main():
    fnames = sys.argv[1:]
    if len(fnames) < 2:
        raise Exception('Need at least 2 line list CSV files')
    counters = []
    for fname in fnames:
        counters.append(parse(fname))
    o2d = []
    for (i, _) in enumerate(counters):
        if i == 0:
            continue
        for characteristics in counters[i].keys():
            # Count the number of new deaths reported on this day
            new_deaths = counters[i][characteristics] - \
                     counters[i - 1].get(characteristics, 0)
            o = calc_o2d(fnames[i], characteristics)
            o2d.extend([o] * new_deaths)
    # Ignore onset-to-death times of 0 days, because these are likely cases where
    # the date of onset was not known and filled out with the date of death
    o2d = list(filter(lambda x: x > 0, o2d))
    print(f'Onset-to-death times (in days): {o2d}')
    print(f'Number of deaths: {len(o2d)}')
    # Fit in a Gamma distribution. Note that we fix the location to 0.
    shape, loc, scale = stats.gamma.fit(o2d, floc=0)
    print(f'Gamma distribution params:\nmean = {shape * scale:.1f}\nshape = {shape:.2f}')
    gen_chart(o2d, shape, loc, scale)

if __name__ == "__main__":
    main()
