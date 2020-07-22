#!/usr/bin/python3
#
# Forecasts Florida COVID-19 deaths from line list case data and CFR stratified by age.

import sys, os, math, datetime, requests
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
date_of_death_url = url = "https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/ArcGIS/rest/services/Florida_COVID_19_Deaths_by_Day/FeatureServer/0/query?where=ObjectId>0&objectIds=&time=&resultType=standard&outFields=*&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="

# Actual deaths
csv_actual_deaths = 'data_deaths/fl_resident_deaths.csv'

# Mean time (in days) from onset of symptoms to death, calculated by gamma.py
o2d = 17.5

# Number of days to calculate the centered moving average of the chart curves
cma_days = 7

datadir = 'data_fdoh'
opts = {}

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
                (0, 29):  0.047 / 100,
                (30, 39): 0.128 / 100,
                (40, 49): 0.199 / 100,
                (50, 59): 0.553 / 100,
                (60, 69): 2.007 / 100,
                (70, 79): 5.699 / 100,
                (80, 89): 14.678 / 100,
                (90, 199): 24.648 / 100,
                }
            ),
        ]

def parse_date(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()

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

def init_chart(date_of_data):
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
        'Source: https://github.com/mbevand/florida-covid19-line-list-data    '
        'Created by: Marc Bevand — @zorinaq',
        transform=ax.transAxes, fontsize='x-small', verticalalignment='top',
    )
    fig.suptitle(f'Forecast of daily COVID-19 deaths in Florida\n(as of {date_of_data})')
    return (fig, ax)

def plot_yyg(ax, last_forecast):
    fname = list(filter(lambda x: x.endswith('.csv'), sorted(os.listdir('utils'))))[-1]
    fnamedate = fname.split('.')[0].split('_')[-1]
    fname = 'utils' + os.sep + fname
    print(f'Opening {fname}')
    df = pd.read_csv(fname)
    df = df[df['date'] <= str(last_forecast)]
    dates = [parse_date(x) for x in df['date']]
    styles = {'linewidth': 1.0, 'linestyle': ':', 'color': (0, .6, .6), 'alpha': 0.7}
    ax.plot(dates, df['projected'], **styles,
            label=f'For comparison only: YYG forecast as of {fnamedate} (3 dashed lines show '
            'projected deaths, lower bound, upper bound)\nhttps://covid19-projections.com/us-fl')
    ax.plot(dates, df['lower'], **styles, label='_nolegend_')
    ax.plot(dates, df['upper'], **styles, label='_nolegend_')

def gen_chart(date_of_data, fig, ax, deaths, deaths_reported_date, deaths_actual_date):
    # plot forecast
    for (i, d) in enumerate(deaths):
        d = cma(d)
        if i == 0:
            last_forecast = d[-1][0]
        ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=1.0,
                label=f'Model {i + 1}: {cfr_models[i].source}')
    # plot YYG's forecast
    plot_yyg(ax, last_forecast)
    # plot actual deaths
    d = cma(deaths_reported_date)
    if 'redline' in opts:
        truncate = date_of_data - datetime.timedelta(days=round(cma_days / 2))
        split = list(filter(lambda x: x[1][0] == truncate, enumerate(d)))[0][0]
        d2 = d[split:]
        d = d[:split + 1]
        hndl, = ax.plot([x[0] for x in d2], [x[1] for x in d2], linewidth=2.0, color=(1, 0, 0, 1.0))
        ax.fill_between([x[0] for x in d2], [x[1] for x in d2], color=(1, 0, 0, 0.15))
        first_legend = ax.legend(handles=[hndl], loc='center', fontsize='small',
                labels=['Actual deaths that occurred\nafter forecast was made'])
        fig.gca().add_artist(first_legend)
    ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=2.0, color=(0, 0, 0, 0.7),
            label=f'Actual deaths by reported date ({cma_days}-day centered moving average)')
    d = deaths_actual_date
    ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=2.0, color=(0.5, 0, 0.5, 0.7),
            label=f'Actual deaths by date of death (note: recent days [in red] may be revised considerably upwards)\nhttps://covid19-usflibrary.hub.arcgis.com/')
    lag = 10
    ax.fill_between([x[0] for x in d[:-lag]], [x[1] for x in d[:-lag]], color=(0, 0, 0, 0.15))
    ax.fill_between([x[0] for x in d[-lag:]], [x[1] for x in d[-lag:]], color=(1.0, 0, 0, 0.15))
    # chart
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=datetime.date(2020, 3, 16), right=last_forecast)
    ax.legend(fontsize='xx-small', bbox_to_anchor=(1, -0.31), frameon=False)
    fig.savefig('forecast_deaths.png', bbox_inches='tight')

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-redline':
        # ignore. author's custom switch to make redline charts updating my first forecast
        # https://twitter.com/zorinaq/status/1279934357323386880
        opts['redline'] = True
        sys.argv.pop(0)
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
    # assume the filename starts with YYYY-MM-DD
    date_of_data = parse_date(os.path.basename(fname)[:10])
    (fig, ax) = init_chart(date_of_data)
    # deaths[N] is an array of daily deaths forecasted by model "N"
    deaths = [[] for i in range(len(cfr_models))]
    day = first_day
    while day <= last_day:
        ages = list(df[df['date_parsed'] == pd.Timestamp(day)]['Age'])
        future_day = day + datetime.timedelta(days=np.round(o2d))
        for (i, model) in enumerate(cfr_models):
            deaths[i].append((future_day, forecast_deaths(model, ages)))
        day += datetime.timedelta(days=1)
    # get actual deaths
    deaths_reported_date = []
    print(f'Opening {csv_actual_deaths}')
    df = pd.read_csv(csv_actual_deaths)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    cumulative_deaths = 0
    for (_, row) in df[df['state'] == 'Florida'].iterrows():
        # gamma.py assumes that the line list CSV file (updated every morning Eastern time)
        # contains data for the day prior: new deaths detected in the file actually
        # occured the day before the CSV file was updated. It is the same thing for
        # the NYT CSV file, so in order to be perfectly consistent, we subtract 1 day here.
        deaths_reported_date.append((row['date'].date() - datetime.timedelta(days=1),
            row['deaths'] - cumulative_deaths))
        cumulative_deaths = row['deaths']
    deaths_actual_date = []
    JSONContent = requests.get(date_of_death_url).json()
    df = pd.DataFrame([row['attributes'] for row in JSONContent['features']])
    df['Date'] = pd.to_datetime(df.Date, unit='ms')
    for (_, row) in df.iterrows():
        deaths_actual_date.append((row['Date'].date(), row["Deaths"]))
    # generate chart
    gen_chart(date_of_data, fig, ax, deaths, deaths_reported_date, deaths_actual_date)

if __name__ == '__main__':
    main()
