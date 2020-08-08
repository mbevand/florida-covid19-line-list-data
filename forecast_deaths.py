#!/usr/bin/python3
#
# Forecasts Florida COVID-19 deaths from line list case data and CFR stratified by age.

import sys, os, math, datetime, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib import rcParams

# Florida COVID-19 line list data. CSV found at:
# https://www.arcgis.com/home/item.html?id=4cc62b3a510949c7a8167f6baa3e069d
csv_url = 'https://www.arcgis.com/sharing/rest/content/items/4cc62b3a510949c7a8167f6baa3e069d/data'

# Observed deaths, by date reported
csv_deaths_reported = 'data_deaths/fl_resident_deaths.csv'

# Observed deaths, by date death occurred
csv_deaths_occurred = 'data_deaths/deaths_by_date_of_death.csv'

# Do not chart last 10 days of deaths by date of death (data is incomplete)
deaths_occurred_ignore_days = 10

# Mean time (in days) from onset of symptoms to death, calculated by gamma.py
o2d = 19.5

# Number of days to calculate the simple moving average of the chart curves
avg_days = 7

datadir = 'data_fdoh'
opts = {}

# Each instance represents one model of age-stratified Case Fatality Ratios
class CFRModel():
    def __init__(self, model_no, source, cfr_average, cfr_by_age):
        self.model_no = model_no
        self.source = source
        self.cfr_average = cfr_average
        self.cfr_by_age = cfr_by_age

cfr_models = [
        #CFRModel(
        #    '1',
        #    'The Epidemiological Characteristics of an Outbreak of 2019 Novel Coronavirus Diseases (COVID-19) — China, 2020\n'
        #    'http://weekly.chinacdc.cn/en/article/doi/10.46234/ccdcw2020.032',
        #    # from table 1, Case fatality rate
        #    2.3 / 100, {
        #        (0, 9):   0 / 100,
        #        (10, 19): 0.2 / 100,
        #        (20, 29): 0.2 / 100,
        #        (30, 39): 0.2 / 100,
        #        (40, 49): 0.4 / 100,
        #        (50, 59): 1.3 / 100,
        #        (60, 69): 3.6 / 100,
        #        (70, 79): 8.0 / 100,
        #        (80, 199): 14.8 / 100,
        #        }
        #    ),
        CFRModel(
            '2',
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
        #CFRModel(
        #    '3',
        #    'Report from Istituto Superiore di Sanità (ISS) based on 73 780 cases\n'
        #    'https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf',
        #    # from table 1, Casi totali, % Letalità
        #    9.2 / 100, {
        #        (0, 29):  0 / 100,
        #        (30, 39): 0.3 / 100,
        #        (40, 49): 0.7 / 100,
        #        (50, 59): 1.7 / 100,
        #        (60, 69): 5.7 / 100,
        #        (70, 79): 16.9 / 100,
        #        (80, 89): 24.6 / 100,
        #        (90, 199): 24.0 / 100,
        #        }
        #    ),
        CFRModel(
            '4',
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
            '5',
            'Our CFR calculated on the Florida line list (age_stratified_cfr.py)',
            1.605 / 100, {
                (0, 29):  0.040 / 100,
                (30, 39): 0.110 / 100,
                (40, 49): 0.220 / 100,
                (50, 59): 0.582 / 100,
                (60, 69): 2.140 / 100,
                (70, 79): 6.606 / 100,
                (80, 89): 17.108 / 100,
                (90, 199): 27.363 / 100,
                }
            ),
        ]

def parse_date(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()

def cfr_for_age(model, age):
    # Given a patient age, return the Case Fatality Ratio for their age
    if math.isnan(age) or age < 0:
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

def sma(arr, avg_days=avg_days):
    # Calculate N-day Simple Moving Average on array:
    #   [('2020-01-01', 1), ('2020-01-02', 2)]
    arr2 = []
    i = avg_days - 1
    while i < len(arr):
        vals = [x[1] for x in arr[i - avg_days + 1:i + 1]]
        arr2.append((arr[i][0], np.mean(vals)))
        i += 1
    return arr2

def init_chart(date_of_data):
    rcParams['figure.titlesize'] = 'x-large'
    (fig, ax) = plt.subplots(dpi=300)#, figsize=(6.4, 6.4)) # default is 6.4 × 4.8
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=7)) # tick every 7 days
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(base=5))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(base=20))
    ax.spines['top'].set_visible(False)
    fig.autofmt_xdate()
    ax.tick_params(axis='x', which='both', labelsize='x-small')
    ax.grid(True, which='major', axis='both', linewidth=0.3)
    ax.grid(True, which='minor', axis='both', linewidth=0.1)
    ax.text(
        -0.050, -0.19,
        'Forecast based on the age of every individual COVID-19 case reported by the Florida Department of Health\n'
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
    styles = {'linewidth': 1.0, 'linestyle': (0, (1, 3)), 'color': 'tab:pink', 'alpha': 1.0}
    ax.plot(dates, df['projected'], **styles,
            label=f'For comparison only: YYG forecast as of {fnamedate} (3 lines show '
            'projected deaths, lower bound, upper bound)\nhttps://covid19-projections.com/us-fl')
    ax.plot(dates, df['lower'], **styles, label='_nolegend_')
    ax.plot(dates, df['upper'], **styles, label='_nolegend_')

def gen_chart(date_of_data, fig, ax, deaths, deaths_reported, deaths_occurred, deaths_occurred_adj, deaths_best_guess):
    # plot observed deaths, by date reported
    d = deaths_reported
    if 'redline' in opts:
        # when line list is published on date_of_data, observed deaths are known up to 1 day prior
        truncate = date_of_data - datetime.timedelta(days=1)
        split = list(filter(lambda x: x[1][0] == truncate, enumerate(d)))[0][0]
        d2 = d[split:]
        d = d[:split + 1]
        hndl, = ax.plot([x[0] for x in d2], [x[1] for x in d2], linewidth=1.5, color=(1, 0, 0, 1.0))
        ax.fill_between([x[0] for x in d2], [x[1] for x in d2], color=(1, 0, 0, 0.15))
        first_legend = ax.legend(handles=[hndl], loc='center', fontsize='small',
                labels=['Observed deaths that occurred\nafter forecast was made'])
        fig.gca().add_artist(first_legend)
    ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=1.5, color=(0, 0, 0, 0.7),
            label=f'Observed deaths by date reported on COVID-19 dashboard ({avg_days}-day SMA)')
    ax.fill_between([x[0] for x in d], [x[1] for x in d], color=(0, 0, 0, 0.10))
    # plot observed deaths, by date death occurred
    d = deaths_occurred
    ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=.75, color=(0, 0, 0, 0.7),
            label=f'Observed deaths by exact date of death ("Deaths by Day", {avg_days}-day SMA); '
            f'last {deaths_occurred_ignore_days} days not charted due to incomplete data')
    d = deaths_occurred_adj
    ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=.75, color=(0, 0, 0, 0.7), ls=(0, (12, 2)),
            label=f'Observed deaths by exact date of death, adjusted for incomplete data')
    # plot best guess
    d = deaths_best_guess
    ax.fill_between([x[0] for x in d], [x[1] for x in d], [x[2] for x in d],
            color='black', alpha=0.10, hatch='\\' * 5, label=f'Forecast of deaths by date reported (best guess)')
    # plot forecasts
    lstyles = ('dashed', 'dashdot', (0, (1, 0.7)))
    for (i, d) in enumerate(deaths):
        if i == 0:
            last_forecast = d[-1][0]
        ax.plot([x[0] for x in d], [x[1] for x in d], linewidth=1.0, ls=lstyles[i % len(lstyles)],
                label=f'Forecast model {cfr_models[i].model_no}: {cfr_models[i].source}')
    # plot YYG's forecast
    plot_yyg(ax, last_forecast)
    # chart
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=datetime.date(2020, 3, 16), right=last_forecast)
    # make "best guess" the first legend entry
    handles, labels = fig.gca().get_legend_handles_labels()
    order = list(range(len(handles)))
    order = [order[-1]] + order[:-1]
    ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
        fontsize='xx-small', bbox_to_anchor=(1, -0.25), frameon=False, handlelength=5)
    fig.savefig('forecast_deaths.png', bbox_inches='tight')

def best_guess(date_of_data, deaths_forecasts, deaths_reported):
    # when line list is published on date_of_data, observed deaths are known up to 1 day prior
    date_of_data -= datetime.timedelta(days=1)
    # find deaths observed on date_of_data
    for date, deaths in deaths_reported:
        if date == date_of_data:
            deaths_target = deaths
            break
    # find model 5 (our model) in deaths_forecasts:
    for (i, _) in enumerate(cfr_models):
        if cfr_models[i].model_no == '5':
            model_5 = deaths_forecasts[i]
    # find model 5 prediction for the last day on which deaths were observed
    for date, deaths in model_5:
        if date == date_of_data:
            model_5_deaths = deaths
            break
    assert model_5_deaths
    epsilon = .005
    adj_factor_min = adj_factor_max = deaths_target / model_5_deaths
    # our best guess will be model 5 multiplied by adj_factor_{min,max}
    best_guess = []
    for date, deaths in model_5:
        if date >= date_of_data:
            best_guess.append((date, deaths * adj_factor_min, deaths * adj_factor_max))
            if date == date_of_data:
                adj_factor_min *= 0.95
                adj_factor_max *= 1.05
            else:
                adj_factor_min *= 1 - epsilon
                adj_factor_max *= 1 + epsilon
    return best_guess

def occurred():
    print(f'Opening {csv_deaths_occurred}')
    result = []
    for feature in json.load(open(csv_deaths_occurred))['features']:
        attrs = feature['attributes']
        date = datetime.datetime.utcfromtimestamp(attrs['Date'] / 1e3).date()
        deaths = attrs['Deaths']
        # occasionally we see bogus rows with dates from years ago. ignore them
        if date >= datetime.date(2020, 1, 1):
            result.append((date, deaths))
    result = sma(result)
    adj_last = 30 # adjust starting this many days prior to the present day
    assert len(result) > adj_last
    deaths_occurred = result[:-deaths_occurred_ignore_days]
    deaths_occurred_adj = []
    for date, deaths in result[-adj_last:-deaths_occurred_ignore_days]:
        x = (result[-1][0] - date).days
        # The CDF of death reporting (1 - e^(-lamba*x)) gives the approximate fraction
        # of total deaths that are reported x days after the death, see:
        # https://github.com/mbevand/florida-covid19-deaths-by-day/blob/master/README.md#average-reporting-delay
        lamda = 0.1728
        frac_reported = 1 - math.e**(-lamda * x)
        deaths_occurred_adj.append((date, deaths / frac_reported))
    return deaths_occurred, deaths_occurred_adj

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
    last_day = sorted(set(df['date_parsed']))[-1].date()
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
            f = forecast_deaths(model, ages)
            if day == last_day:
                # line list data is almost always incomplete for the last day (FDOH doesn't
                # refresh the file at midnight), so heuristically the forecast deaths for
                # the last day are forced to be at least equal to the day prior
                f = max(f, deaths[i][-1][1])
            deaths[i].append((future_day, f))
        day += datetime.timedelta(days=1)
    for i in range(len(deaths)):
        deaths[i] = sma(deaths[i])
    # get observed deaths, by date reported
    deaths_reported = []
    print(f'Opening {csv_deaths_reported}')
    df = pd.read_csv(csv_deaths_reported)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    cumulative_deaths = 0
    for (_, row) in df[df['state'] == 'Florida'].iterrows():
        # deaths in this CSV file (whose data source is updated every morning Eastern time)
        # contains data for the day prior, so we subtract 1 day
        deaths_reported.append((row['date'].date() - datetime.timedelta(days=1),
            row['deaths'] - cumulative_deaths))
        cumulative_deaths = row['deaths']
    deaths_reported = sma(deaths_reported)
    # get observed deaths, by date death occurred
    deaths_occurred, deaths_occurred_adj = occurred()
    # calculate best guess forecast
    deaths_best_guess = best_guess(date_of_data, deaths, deaths_reported)
    # generate chart
    gen_chart(date_of_data, fig, ax, deaths, deaths_reported, deaths_occurred, deaths_occurred_adj, deaths_best_guess)

if __name__ == '__main__':
    main()
