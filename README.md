# Analyzing age trends of COVID-19 cases in Florida

*Updated: 26 June 2020*

Author: Marc Bevand

The Florida Department of Health has an **amazing** dataset here: [complete line
list data of the state's COVID-19 cases][dataset], including age information
for all 100k+ cases! My script processes that data:

1. Browse the [line list data][dataset] page
1. Click `Download → Spreadsheet` to download the CSV file
1. Place the CSV file in this directory and name it `Florida_COVID19_Case_Line_Data.csv`
1. Run `./process.py`

This creates a heatmap (`heatmap.png`) representing the number of cases by age bracket over time:

![Heatmap of COVID-19 cases in Florida](heatmap_published.png)

By default the size of each pixel, or *bucket*, is 10-year age brackets and 7-day
time periods. This can be changed by editing the variables `buckets_ages` and `buckets_days`.

The script also produces a numerical summary:

```
$ ./process.py
Number of COVID-19 cases per 7-day time period in Florida by age bracket over time:
period,     00-09, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70-79, 80-89, 90-199, median_age
2020-02-29,     0,     0,     2,     0,     0,     2,     3,     2,     0,     0,  63.0
2020-03-07,     0,     0,     4,     2,     5,     8,    18,    11,     2,     0,  65.0
2020-03-14,     2,    18,    76,    62,    80,    83,   105,    63,    26,     8,  53.0
2020-03-21,    13,    63,   370,   441,   442,   515,   399,   350,   155,    33,  51.0
2020-03-28,    49,   126,   948,  1146,  1228,  1330,  1109,   774,   358,    80,  50.0
2020-04-04,    53,   148,   881,  1179,  1265,  1418,  1214,   747,   438,   138,  51.0
2020-04-11,    76,   186,   834,   982,  1169,  1268,   970,   647,   402,   168,  50.0
2020-04-18,    85,   200,   706,   904,   860,  1039,   804,   553,   441,   229,  51.0
2020-04-25,    65,   175,   596,   703,   682,   804,   632,   458,   388,   179,  51.0
2020-05-02,    70,   175,   624,   661,   665,   676,   541,   437,   399,   180,  50.0
2020-05-09,    86,   183,   653,   728,   710,   753,   580,   428,   388,   149,  49.0
2020-05-16,   202,   301,   796,   958,   891,   867,   628,   448,   361,   171,  46.0
2020-05-23,   159,   344,   849,   968,   886,   773,   533,   311,   253,    98,  42.0
2020-05-30,   318,   589,  1180,  1292,  1127,   989,   718,   405,   253,   133,  41.0
2020-06-06,   449,   804,  2436,  2025,  1570,  1451,   933,   525,   366,   174,  38.0
2020-06-13,   692,  1502,  5225,  3735,  2812,  2384,  1450,   840,   446,   164,  35.0
2020-06-20,   730,  1790,  6294,  4283,  3114,  2634,  1499,   858,   437,   173,  34.0
(Last period's data is incomplete. Age unknown for 139 out of 114018 cases)
```

[dataset]: https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data

# Analysis

The number of cases is increasing among *all* age brackets. However the median age of
cases is declining because younger people appear to be driving increased transmission,
especially the 20-24 age bracket.

# Miscellaneous

`sort.py` is a tool that strips the `ObjectId` column from the CSV file and sorts the
rows. This is helpful to compare 2 CSV files published on 2 different days, because
the `ObjectId` value and the order of rows are not stable from one file to another.
