# Analyzing age trends of COVID-19 cases in Florida

*Updated: 23 June 2020*

Author: Marc Bevand

The Florida Department of Health has an **amazing** dataset here: [complete line
list data of the state's COVID-19 cases][dataset], including age information
for all 100k+ cases! My script processes that data:

1. Browse the [line list data][dataset] page
1. Click `Download → Spreadsheet` to download the CSV file
1. Place the CSV file in this directory and name it `Florida_COVID19_Case_Line_Data.csv`
1. Run `./process.py`

Result:
```
$ ./process.py
Number of COVID-19 cases per week in Florida, by age bracket.
Source: https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data

week_of,    00-09, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70-79, 80-89, 90-199, median_age
2020-03-02,     0,     0,     2,     0,     0,     2,     5,     5,     0,     0,  65.5
2020-03-09,     0,     8,    15,    10,    18,    15,    34,    17,     6,     0,  57.0
2020-03-16,     2,    27,   137,   135,   145,   174,   165,   112,    59,    12,  52.0
2020-03-23,    21,    70,   522,   631,   659,   727,   552,   456,   210,    43,  50.0
2020-03-30,    55,   139,   967,  1212,  1252,  1408,  1189,   819,   362,    86,  50.0
2020-04-06,    60,   165,   888,  1100,  1280,  1396,  1198,   731,   433,   172,  51.0
2020-04-13,    67,   175,   748,   971,  1049,  1173,   877,   614,   404,   170,  50.0
2020-04-20,    92,   223,   734,   877,   867,   989,   745,   505,   438,   216,  50.0
2020-04-27,    66,   164,   602,   680,   693,   788,   674,   498,   412,   190,  52.0
2020-05-04,    62,   153,   562,   634,   616,   647,   495,   393,   379,   162,  50.0
2020-05-11,   125,   235,   792,   892,   785,   878,   656,   457,   407,   163,  48.0
2020-05-18,   195,   331,   805,   913,   903,   790,   580,   387,   315,   140,  45.0
2020-05-25,   178,   352,   842,   966,   872,   789,   542,   335,   232,   103,  42.0
2020-06-01,   363,   635,  1441,  1441,  1217,  1137,   753,   437,   293,   142,  40.0
2020-06-08,   526,   931,  2916,  2354,  1824,  1584,  1022,   566,   364,   168,  37.0
2020-06-15,   766,  1815,  6398,  4440,  3277,  2793,  1640,   953,   491,   191,  34.0
2020-06-22,   134,   336,   990,   758,   579,   462,   304,   153,   124,    41,  35.0
(Last week's data is incomplete. Age unknown for 72 out of 103431 cases)
```

[dataset]: https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data

# Analysis

The number of cases is increasing among *all* age brackets. However the median age of
cases is declining because younger people, especially in the age bracket 20-29, account
for the largest share of the daily case growth.
