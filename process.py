#!/usr/bin/python3
#
# Analyzes Florida line list data available at (click Download → Spreadsheet):
# https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
#
# Direct link: https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv

import sys, csv, datetime, statistics

age_buckets = [
        (0,9),
        (10,19),
        (20,29),
        (30,39),
        (40,49),
        (50,59),
        (60,69),
        (70,79),
        (80,89),
        (90,199),
        ]

class Buckets():
    # cases_per_bracket[23][(80,89)] is the number of cases for week 23 in the age bracket 80-89
    cases_per_bracket = {}
    # ages[23] is the list of case ages for week 23
    ages = {}
    age_unknown = 0
    total_cases = 0

def week2monday(week):
    # convert ISO week number to the date of the Monday in that week
    return datetime.datetime.strptime('2020 {} 1'.format(week), '%G %V %u').date()

def bucket(b, age, date):
    # get the ISO week number from the date
    week = date.isocalendar()[1]
    if week not in b.cases_per_bracket:
        b.cases_per_bracket[week] = {x: 0 for x in age_buckets}
        b.ages[week] = []
    for x in age_buckets:
        if age >= x[0] and age <= x[1]:
            b.cases_per_bracket[week][x] += 1
    b.ages[week].append(age)

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
        b.total_cases += 1
        if Age == 'NA':
            b.age_unknown += 1
            continue
        # ChartDate is the date the case was counted according the header of table
        # "Coronavirus: line list of cases" in
        # http://ww11.doh.state.fl.us/comm/_partners/action/report_archive/state/state_reports_latest.pdf
        date = datetime.datetime.strptime(ChartDate.split(' ')[0], '%Y/%m/%d').date()
        age = int(Age)
        bucket(b, age, date)
    return b

def show_stats(b):
    print('''Number of COVID-19 cases per week in Florida, by age bracket.
    Source: https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
    ''')
    sys.stdout.write('{:11}'.format('week_of,'))
    for x in age_buckets:
        sys.stdout.write(' {:02d}-{:02d},'.format(x[0], x[1]))
    sys.stdout.write(' median_age\n')
    for week in sorted(b.cases_per_bracket):
        sys.stdout.write('{:10},'.format(str(week2monday(week))))
        for x in age_buckets:
            sys.stdout.write(' {:5d},'.format(b.cases_per_bracket[week][x]))
        sys.stdout.write('  {:.1f}\n'.format(statistics.median(b.ages[week])))
    print("(Last week's data is incomplete. Age unknown for {} out of {} cases)".format(b.age_unknown, b.total_cases))

def main():
    b = parse()
    show_stats(b)

if __name__ == '__main__':
    main()
