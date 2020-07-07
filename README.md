# Forecasting deaths and analyzing age trends of COVID-19 cases in Florida

*Updated: 06 July 2020*

Authors: Marc Bevand, Michael A. Alcorn

The Florida Department of Health has an **amazing** dataset here: [complete line
list data of the state's COVID-19 cases][dataset], including age information
for all 150k+ cases! We provide two scripts:
* `forecast_deaths.py` forecasts deaths based on age-stratified Case Fatality Ratios (CFR)
* `heatmap.py` creates a heatmap representing the number of cases by age bracket over time

## Forecasting deaths

![Forecast of daily COVID-19 deaths in Florida](forecast_deaths_published.png)

`forecast_deaths.py` does not rely on death data, but relies
**solely** on case ages, date of first symptoms, and published age-stratified CFR
estimates.

The script starts by downloading the [FDOH line list dataset][dataset]. This gives us
(1) the age of every case diagnosed with COVID-19, and (2) the date of first symptoms
(`EventDate` CSV column.)

Then it multiplies the number of cases by age bracket with age-stratified Case Fatality Ratios issued from 4 independent models:

1. [The Epidemiological Characteristics of an Outbreak of 2019 Novel Coronavirus Diseases (COVID-19) — China, 2020][m1] (table 1, Case fatality rate)
1. [Estimates of the severity of coronavirus disease 2019: a model-based analysis][m2] (table 1, CFR, Adjusted for censoring, demography, and under-ascertainment)
1. [https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf][m3] (table 1, Casi totali, % Letalità)
1. [Case fatality risk by age from COVID-19 in a high testing setting in Latin America: Chile, March-May, 2020][m4] (table 2, Latest estimate)

Then it assumes death occurs on average 17.8 days after infection, which is the mean onset-to-death time reported in
[Estimating the effects of nonpharmaceutical interventions on COVID-19 in Europe, Supplementary information, page 4][o2d].

The end result is a simple and accurate forecast that can not only
estimate deaths up to ~18 days ahead of time, but can also estimate *past*
deaths: notice how the colored curves produced by the model follow closely the
black curve (actual deaths.)

Actual deaths are fetched from the [New York Times Covid-19 data repository][nyt] and
are only used to draw the black curve. They are *not* used as part of the forecast.

The forecast curves and actual death curve are smoothed with a 7-day centered moving average.

Since the forecast uses line list data, ie. *detected* cases, it is important that
we feed it CFR estimates, not IFR estimates. Infection Fatality Ratios take
into account *undetected* cases and thus would not be consistent with line
list data.

## Heatmap of age over time

`heatmap.py` downloads the dataset automatically, creates the heatmap
(`heatmap.png`) and also produces a numerical summary:

![Heatmap of COVID-19 cases in Florida](heatmap_published.png)

```
$ ./heatmap.py
Downloading from https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv...
Number of COVID-19 cases per 4-day time period in Florida by age bracket over time:
period_start, 00-04, 05-09, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85-89, 90-199, median_age
  2020-03-02,     0,     0,     0,     0,     1,     1,     0,     0,     0,     0,     1,     1,     2,     1,     2,     0,     0,     0,     0,  63.0
  2020-03-06,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     1,     0,     2,     3,     0,     3,     1,     0,     0,  66.5
  2020-03-10,     0,     0,     0,     0,     2,     2,     1,     1,     1,     4,     3,     4,     3,    10,     6,     2,     1,     0,     0,  63.5
  2020-03-14,     0,     0,     0,    13,    12,    11,     6,    13,    13,    14,    11,    13,    17,    20,    13,    13,     5,     4,     1,  52.0
  2020-03-18,     0,     2,     3,    12,    50,    38,    40,    27,    26,    53,    43,    55,    51,    52,    31,    30,    26,    13,     9,  53.0
  2020-03-22,     7,     3,     7,    22,    78,    85,   114,   102,   103,   117,   115,   128,    95,    99,    89,    79,    49,    12,    11,  50.0
  2020-03-26,     6,     5,    10,    38,   180,   216,   247,   225,   245,   246,   289,   254,   207,   194,   186,   136,   109,    55,    34,  50.0
  2020-03-30,    20,    13,    15,    59,   241,   308,   350,   331,   331,   395,   377,   404,   348,   309,   287,   182,   110,    75,    48,  50.0
  2020-04-03,    19,     9,    21,    66,   230,   322,   398,   335,   345,   388,   438,   411,   381,   368,   256,   212,   159,    89,    49,  51.0
  2020-04-07,    17,    16,    24,    65,   228,   276,   326,   314,   344,   395,   407,   401,   365,   321,   240,   180,   161,   110,   107,  51.0
  2020-04-11,    18,    19,    24,    65,   196,   246,   231,   258,   268,   338,   331,   328,   308,   243,   191,   136,   111,    86,    87,  51.0
  2020-04-15,    26,    21,    27,    93,   192,   264,   302,   308,   307,   372,   368,   396,   292,   248,   212,   180,   138,   104,   114,  50.0
  2020-04-19,    25,    19,    34,    64,   155,   215,   246,   231,   215,   224,   266,   269,   230,   178,   168,   163,   144,   115,   123,  52.0
  2020-04-23,    28,    24,    40,   105,   220,   244,   248,   282,   239,   286,   295,   276,   240,   177,   140,   122,   121,   114,   116,  48.0
  2020-04-27,    16,    19,    29,    49,   138,   172,   186,   201,   175,   190,   224,   239,   203,   186,   135,   128,   114,   119,   117,  53.0
  2020-05-01,    21,    19,    28,    92,   161,   210,   179,   181,   179,   217,   212,   202,   187,   171,   157,   146,   136,   112,   105,  51.0
  2020-05-05,    19,    22,    25,    61,   159,   188,   211,   186,   175,   190,   169,   212,   152,   131,   107,   110,   112,   104,    94,  49.0
  2020-05-09,    21,    25,    19,    77,   159,   214,   220,   182,   185,   226,   204,   207,   180,   137,   135,   102,   103,    90,    66,  48.0
  2020-05-13,    36,    36,    42,    95,   189,   246,   266,   264,   227,   239,   275,   281,   223,   168,   164,   129,   148,   117,   112,  49.0
  2020-05-17,    55,    57,    57,   100,   209,   240,   256,   260,   223,   254,   202,   209,   175,   147,   125,   112,   106,   101,   100,  45.0
  2020-05-21,    53,    49,    68,   141,   227,   249,   271,   256,   253,   264,   219,   247,   188,   158,    89,    96,    76,    74,    61,  44.0
  2020-05-25,    43,    42,    57,   115,   201,   248,   290,   255,   245,   243,   197,   238,   169,   123,    97,    83,    82,    66,    60,  43.0
  2020-05-29,    50,    62,    84,   138,   234,   247,   267,   260,   247,   234,   212,   232,   182,   142,    95,   106,    65,    53,    65,  42.0
  2020-06-02,   121,   115,   143,   281,   367,   447,   436,   463,   378,   396,   337,   323,   268,   198,   154,   105,    92,    81,    87,  40.0
  2020-06-06,   111,   104,   120,   236,   509,   522,   472,   401,   339,   370,   374,   343,   256,   188,   149,   112,    96,    85,    82,  39.0
  2020-06-10,   169,   171,   196,   415,  1034,   915,   823,   734,   585,   586,   558,   466,   389,   277,   205,   150,   134,    96,   107,  36.0
  2020-06-14,   185,   165,   188,   511,  1332,  1171,  1047,   870,   748,   718,   635,   587,   448,   307,   269,   193,   138,   105,    85,  36.0
  2020-06-18,   264,   227,   305,   942,  2414,  1946,  1575,  1286,  1037,  1044,   930,   856,   578,   427,   326,   239,   164,   123,   116,  34.0
  2020-06-22,   386,   349,   411,  1468,  3571,  3095,  2576,  2004,  1692,  1659,  1522,  1251,   948,   685,   514,   380,   274,   194,   189,  34.0
  2020-06-26,   537,   446,   487,  1756,  4001,  3737,  3110,  2714,  2259,  2172,  2104,  1772,  1364,  1039,   734,   493,   349,   293,   214,  36.0
(Last period's data may be incomplete. Age unknown for 225 out of 152434 cases.)
```

The number of cases is increasing among *all* age brackets. However the median age of
cases is declining because younger people appear to be driving increased transmission,
especially the 20-24 age bracket.

By default the size of each pixel, or *bucket*, is 5-year age brackets and 4-day
time periods. This can be changed by editing the variables `buckets_ages` and `buckets_days`.

For efficiency, you may download the CSV manually once, and pass it as an argument
to the script:

1. Browse the [line list data][dataset] page
1. Click `Download → Spreadsheet` to download the CSV file
1. Run `./heatmap.py <path-to-csv-file>`

## Miscellaneous

`heatmap.py` also creates `heatmap_age_share.png`: the pixel intensity represents
not the number of cases, but the share of cases in this age bracket among all
cases reported in this time period.

`sort.py` is a tool that strips the `ObjectId` column from the CSV file and sorts the
rows. This is helpful to compare 2 CSV files published on 2 different days, because
the `ObjectId` value and the order of rows are not stable from one file to another.

[dataset]: https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
[nyt]: https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv
[o2d]: https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-020-2405-7/MediaObjects/41586_2020_2405_MOESM1_ESM.pdf
[m1]: http://weekly.chinacdc.cn/en/article/doi/10.46234/ccdcw2020.032
[m2]: https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30243-7/fulltext
[m3]: https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf
[m4]: https://www.medrxiv.org/content/10.1101/2020.05.25.20112904v1
