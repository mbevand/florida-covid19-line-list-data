#!/usr/bin/python3
#
# Fetch YYG's daily death projections for Florida, and outputs them in CSV format

import requests, json

data = {}

def no_none(s):
    return '' if s is None else str(s)

def store(column, l):
    for date, n in l:
        if date not in data:
            data[date] = {}
        data[date][column] = n

def main():
    r = requests.get('https://covid19-projections.com/us-fl')
    r.raise_for_status()
    # Javascript to parse (2 occurrences of "Plotly.newPlot, we want the 1st):
    #   Plotly.newPlot(
    #     '979da293-335c-469a-a64c-281e2fa4a4bf',
    #     [{"hoverinfo": "skip", " ...
    #     ...],
    # Extract text between the square brackets
    i = r.text.index('Plotly.newPlot')
    i = r.text.index('[', i)
    j = r.text.index('],\n', i)
    ploty = json.loads(r.text[i : j + 1])
    #print(json.dumps(ploty))
    for i, dataset in enumerate(ploty):
        #print(f'dataset {i}: {dataset}')
        # The datasets are used to draw 3 plots: yaxis is "y" or "y2" or "y3"
        # y is Deaths per day
        # y2 and y3 are Total deaths and Reproduction number
        if dataset['yaxis'] == 'y' and 'hovertemplate' in dataset:
            if 'lower range' in dataset['hovertemplate']:
                store('lower', list(zip(dataset['x'], dataset['y'])))
            if 'upper range' in dataset['hovertemplate']:
                store('upper', list(zip(dataset['x'], dataset['y'])))
            if 'projected' in dataset['hovertemplate']:
                store('projected', list(zip(dataset['x'], dataset['y'])))
    for date in data:
        if data[date]['lower']:
            break
    first_date = date
    f = open(f'yyg_us-fl_daily_deaths_{first_date}.csv', 'w')
    f.write(f'date,lower,projected,upper\n')
    for date in sorted(data.keys()):
        f.write(','.join((date,
            no_none(data[date]["lower"]),
            no_none(data[date]["projected"]),
            no_none(data[date]["upper"]))) + '\n')

if __name__ == '__main__':
    main()
