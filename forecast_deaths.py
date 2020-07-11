#!/usr/bin/python3
#
# Forecasts Florida COVID-19 deaths from line list case data and CFR stratified by age.

import sys, os, math, datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib import rcParams

# Florida COVID-19 line list data. CSV found at:
# https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
# (click Download → Spreadsheet)
csv_url = 'https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv'

# Actual deaths
csv_actual_deaths = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'

# Mean time (in days) from onset of symptoms to death
# Source: Estimating the effects of nonpharmaceutical interventions on COVID-19 in Europe, Supplementary information, page 4:
# https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-020-2405-7/MediaObjects/41586_2020_2405_MOESM1_ESM.pdf
o2d = np.round(17.8)

# Number of days to calculate the centered moving average of the chart curves
cma_days = 7

datadir = 'data_fdoh'

# Each instance represents one model of age-stratified Case Fatality Ratios
class CFRModel():
    def __init__(self, source, cfr_average, cfr_by_age):
        self.source = source
        self.cfr_average = cfr_average
        self.cfr_by_age = cfr_by_age

cfr_models = [
        CFRModel(
            'The Epidemiological Characteristics of an Outbreak of 2019 Novel Coronavirus Diseases (COVID-19) — China, 2020\n'
            'http://weekly.chinacdc.cn/en/article/doi/10.46234/ccdcw2020.032',
            # from table 1, Case fatality rate
            2.3 / 100, {
                (0, 9):   0 / 100,
                (10, 19): 0.2 / 100,
                (20, 29): 0.2 / 100,
                (30, 39): 0.2 / 100,
                (40, 49): 0.4 / 100,
                (50, 59): 1.3 / 100,
                (60, 69): 3.6 / 100,
                (70, 79): 8.0 / 100,
                (80, 199): 14.8 / 100,
                }
            ),
        CFRModel(
            'Estimates of the severity of coronavirus disease 2019: a model-based analysis\n'
            'https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30243-7/fulltext',
            # from table 1, CFR, Adjusted for censoring, demography, and under-ascertainment
            1.38 / 100, {
                (0, 9):   0.00260 / 100,
                (10, 19): 0.0148 / 100,
                (20, 29): 0.0600 / 100,
                (30, 39): 0.146 / 100,
                (40, 49): 0.295 / 100,
                (50, 59): 1.25 / 100,
                (60, 69): 3.99 / 100,
                (70, 79): 8.61 / 100,
                (80, 199): 13.4 / 100,
                }
            ),
        CFRModel(
            'Report from Istituto Superiore di Sanità (ISS) based on 73 780 cases\n'
            'https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf',
            # from table 1, Casi totali, % Letalità
            9.2 / 100, {
                (0, 29):  0 / 100,
                (30, 39): 0.3 / 100,
                (40, 49): 0.7 / 100,
                (50, 59): 1.7 / 100,
                (60, 69): 5.7 / 100,
                (70, 79): 16.9 / 100,
                (80, 89): 24.6 / 100,
                (90, 199): 24.0 / 100,
                }
            ),
        CFRModel(
            'Case fatality risk by age from COVID-19 in a high testing setting in Latin America: Chile, March-May, 2020\n'
            'https://www.medrxiv.org/content/10.1101/2020.05.25.20112904v1',
            # from table 2, Latest estimate
            1.78 / 100, {
                (0, 39):  0.08 / 100,
                (40, 49): 0.61 / 100,
                (50, 59): 1.06 / 100,
                (60, 69): 3.79 / 100,
                (70, 79): 12.22 / 100,
                (80, 199): 26.27 / 100,
                }
            ),
        CFRModel(
            'Our model (age_stratified_cfr.py) based on the FDOH line list',
            # TODO: age_stratified_cfr.py should calculate the average CFR. For now assume it is zero.
            # This does not affect the forecast much because the average CFR is only used with cases
            # of unknown age.
            0.0 / 100, {
                (0, 29):  0.035 / 100,
                (30, 39): 0.125 / 100,
                (40, 49): 0.270 / 100,
                (50, 59): 0.556 / 100,
                (60, 69): 2.123 / 100,
                (70, 79): 6.303 / 100,
                (80, 89): 16.062 / 100,
                (90, 199): 25.720 / 100,
                }
            ),
        ]

def cfr_for_age(model, age):
    # Given a patient age, return the Case Fatality Ratio for their age
    if math.isnan(age):
        # For patients whose age is unknown (less than 1% of all cases),
        # assume the average CFR
        return model.cfr_average
    for (bracket, cfr) in model.cfr_by_age.items():
        if age in range(bracket[0], bracket[1] + 1):
            return cfr
    raise Exception(f'Could not find IFR for age {age} in model {model.source}')

def forecast_deaths(model, ages):
    # Given a list of patient ages, return the expected number of deaths.
    return sum([cfr_for_age(model, a) for a in ages])

def cma(arr, n=cma_days):
    # Calculate n-day Centered Moving Average on array:
    #   [(date1, value1), (date2, value2), ...]
    assert n % 2 == 1
    half = int(n / 2)
    arr2 = []
    i = half
    while i < len(arr) - half:
        vals = [x[1] for x in arr[i - half:i + half + 1]]
        arr2.append((arr[i][0], np.mean(vals)))
        i += 1
    return arr2

def init_chart():
    rcParams['figure.titlesize'] = 'x-large'
    (fig, ax) = plt.subplots(dpi=300)#, figsize=(6.4, 6.4)) # default is 6.4 × 4.8
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=7)) # tick every 7 days
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(base=2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(base=20))
    ax.spines['top'].set_visible(False)
    fig.autofmt_xdate()
    ax.tick_params(axis='x', which='both', labelsize='small')
    ax.grid(True, which='major', axis='both', linewidth=0.3)
    ax.grid(True, which='minor', axis='both', linewidth=0.1)
    ax.text(
        -0.025, -0.19,
        'Forecast based on the age of every individual COVID-19 case reported by the Florida Department of\n'
        f'Health combined with {len(cfr_models)} models of age-stratified Case Fatality Ratios.\n'
        'Source: https://github.com/mbevand/florida-covid19-line-list-data / '
        'Created by: Marc Bevand — @zorinaq',
        transform=ax.transAxes, fontsize='x-small', verticalalignment='top',
    )
    today = str(datetime.datetime.now().date())
    fig.suptitle(f'Forecast of daily COVID-19 deaths in Florida\n(as of {today})')
    return (fig, ax)

def gen_chart(fig, ax, deaths, deaths_actual):
    # plot forecast
    for (i, d) in enumerate(deaths):
        d = cma(d)
        if i == 0:
            last_forecast = d[-1][0]
        ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=1.0,
                label=f'Model {i + 1}: {cfr_models[i].source}')
    # plot actual deaths
    d = cma(deaths_actual)
    ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=2.0, color=(0, 0, 0, 0.7),
            label=f'Actual deaths ({cma_days}-day centered moving average)')
    ax.fill_between([x[0] for x in d], [x[1] for x in d], color=(0, 0, 0, 0.15))
    # chart
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=datetime.date(2020, 3, 16), right=last_forecast)
    ax.legend(fontsize='xx-small', bbox_to_anchor=(1, -0.31), frameon=False)
    fig.savefig('forecast_deaths.png', bbox_inches='tight')

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
    # We estimate deaths based on the mean onset-to-death time, so we must work from EventDate.
    df['date_parsed'] = pd.to_datetime(
            # Timestamps are formatted as "2020/06/28 05:00:00+00". We truncate
            # after the whitespace to ignore the time.
            df['EventDate'].apply(lambda x: x.split(' ')[0]), format='%Y/%m/%d'
    )
    # ignore the last day ([-2] instead of [-1]) because case data from the last day may be incomplete
    last_day = sorted(set(df['date_parsed']))[-2].date()
    first_day = sorted(set(df['date_parsed']))[0].date()
    (fig, ax) = init_chart()
    # deaths[N] is an array of daily deaths forecasted by model "N"
    deaths = [[] for i in range(len(cfr_models))]
    day = first_day
    while day <= last_day:
        ages = list(df[df['date_parsed'] == pd.Timestamp(day)]['Age'])
        future_day = day + datetime.timedelta(days=o2d)
        for (i, model) in enumerate(cfr_models):
            deaths[i].append((future_day, forecast_deaths(model, ages)))
        day += datetime.timedelta(days=1)
    # get actual deaths
    deaths_actual = []
    print(f'Downloading {csv_actual_deaths}')
    df = pd.read_csv(csv_actual_deaths)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    cumulative_deaths = 0
    for (_, row) in df[df['state'] == 'Florida'].iterrows():
        deaths_actual.append((row['date'].date(), row['deaths'] - cumulative_deaths))
        cumulative_deaths = row['deaths']
    # generate chart
    gen_chart(fig, ax, deaths, deaths_actual)

if __name__ == '__main__':
    main()
