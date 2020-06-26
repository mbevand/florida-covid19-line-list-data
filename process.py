#!/usr/bin/python3
#
# Analyzes Florida COVID-19 line list data by age bracket over time.
# Source (click Download → Spreadsheet): https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
# Direct link: https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv

import sys, csv, datetime, statistics, math

class Buckets():
    buckets_ages = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 89), (90, 199)]
    #buckets_ages = [(0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 49), (50, 54), (55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89), (90, 199)]
    buckets_days = 7
    # cases_per_bracket[datetime.date(y,m,d)][(80,89)] is the number of cases for
    # the period of time starting on datetime.date(y,m,d) in the age bracket 80-89
    cases_per_bracket = {}
    # ages[datetime.date(y,m,d)]] is the list of case ages for the period of time
    # starting on datetime.date(y,m,d)
    ages = {}
    # total number of cases
    cases_total = 0
    # number of cases which have no age information
    cases_age_unknown = 0

    def store(self, age, date):
        reference = datetime.date(2020, 1, 4) # arbitrary point in time to align the time periods
        delta = (date - reference).days
        period = reference + datetime.timedelta(days=delta - delta % self.buckets_days)
        if period not in self.cases_per_bracket:
            self.cases_per_bracket[period] = {x: 0 for x in self.buckets_ages}
            self.ages[period] = []
        for x in self.buckets_ages:
            if age >= x[0] and age <= x[1]:
                self.cases_per_bracket[period][x] += 1
        self.ages[period].append(age)

def parse():
    b = Buckets()
    first = True
    for l in csv.reader(open('Florida_COVID19_Case_Line_Data.csv')):
        (County,Age,Age_group,Gender,Jurisdiction,Travel_related,Origin,EDvisit,Hospitalized,Died,Case_,Contact,Case1,EventDate,ChartDate,ObjectId) = l
        if first:
            assert ','.join((County,Age,Age_group,Gender,Jurisdiction,Travel_related,Origin,EDvisit,Hospitalized,Died,Case_,Contact,Case1,EventDate,ChartDate,ObjectId)) == \
                 '\ufeff' + 'County,Age,Age_group,Gender,Jurisdiction,Travel_related,Origin,EDvisit,Hospitalized,Died,Case_,Contact,Case1,EventDate,ChartDate,ObjectId'
            first = False
            continue
        b.cases_total += 1
        if Age == 'NA':
            b.cases_age_unknown += 1
            continue
        # ChartDate is the date the case was counted according the header of table "Coronavirus: line list of cases" in
        # http://ww11.doh.state.fl.us/comm/_partners/action/report_archive/state/state_reports_latest.pdf
        date = datetime.datetime.strptime(ChartDate.split(' ')[0], '%Y/%m/%d').date()
        age = int(Age)
        b.store(age, date)
    return b

def show_stats(b):
    print('Number of COVID-19 cases per {}-day time period in Florida by age bracket over time:'.format(b.buckets_days))
    sys.stdout.write('{:11}'.format('period,'))
    for x in b.buckets_ages:
        sys.stdout.write(' {:02d}-{:02d},'.format(x[0], x[1]))
    sys.stdout.write(' median_age\n')
    for period in sorted(b.cases_per_bracket):
        sys.stdout.write('{:10},'.format(str(period)))
        for x in b.buckets_ages:
            sys.stdout.write(' {:5d},'.format(b.cases_per_bracket[period][x]))
        sys.stdout.write('  {:.1f}\n'.format(statistics.median(b.ages[period])))
    print("(Last period's data is incomplete. Age unknown for {} out of {} cases)".format(
        b.cases_age_unknown, b.cases_total))

def chart(b):
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    from matplotlib import rcParams
    import numpy as np
    rcParams["figure.titlesize"] = 'x-large'
    def fmt_age(x, pos=None):
        if x >= 0 and x < len(b.buckets_ages):
            return '{}-{}'.format(*b.buckets_ages[int(x)])
    def fmt_dates(x, pos=None):
        if x >= 0 and x < len(periods):
            return periods[int(x)]
    fig, ax = plt.subplots(dpi=300)
    periods = sorted(b.cases_per_bracket.keys())
    # exclude last period because its data is incomplete
    periods = periods[:-1]
    a = np.zeros((len(b.buckets_ages), len(periods)))
    for (j, period) in enumerate(periods):
        for (i, bracket) in enumerate(b.buckets_ages):
            # square root makes the heatmap brighter (by dampening the highest values)
            a[i, j] = math.sqrt(b.cases_per_bracket[period][bracket])
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=2))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_dates))
    ax.yaxis.set_major_locator(ticker.MultipleLocator())
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_age))
    fig.autofmt_xdate()
    ax.set_ylabel('Age range')
    ax.tick_params(axis='x', which='both', labelsize='small')
    ax.text(-.1, -.2,
'''Pixel intensity represents number of cases reported per {}-day time period
Source: https://github.com/mbevand/florida-covid19-line-list-data
Created by: Marc Bevand — @zorinaq'''.format(b.buckets_days), transform=ax.transAxes, verticalalignment='top')
    fig.suptitle('Heatmap of COVID-19 cases in Florida by age bracket over time')
    ax.imshow(a, cmap='inferno', origin='lower', interpolation='nearest')
    plt.savefig('heatmap.png', bbox_inches='tight')

def main():
    b = parse()
    show_stats(b)
    chart(b)

if __name__ == '__main__':
    main()
