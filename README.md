# Forecasting deaths and analyzing age trends of COVID-19 cases in Florida

*Updated: 18 July 2020*

Authors: Marc Bevand

The Florida Department of Health (FDOH) has an **amazing** dataset here:
[complete line list of the state's COVID-19 cases and deaths][dataset]. To our
knowledge, it is the only *open* dataset documenting the exact age of hundreds
of thousands of cases. This gives us great insights because age is a very
important factor affecting the Case Fatality Ratio (CFR) of COVID-19. This
repository provides tools to analyze the data:

* [forecast_deaths.py](forecast_deaths.py) forecasts deaths in the state, based on various age-stratified CFR estimates
* [age_stratified_cfr.py](age_stratified_cfr.py) calculates the age-stratified CFR, based on recent deaths in the state
* [gamma.py](gamma.py) calculates the times between onset of symptoms and death (onset-to-death) and fits them in a Gamma distribution
* [heatmap.py](heatmap.py) creates a heatmap representing the number of cases by age bracket evolving over time

## FDOH line list

To download the FDOH line list, browse the [data page][dataset] and click
`Download → Spreadsheet`. We made daily archives of the line list in directory
[data_fdoh](data_fdoh).

The line list is in CSV format and the columns are self-explanatory: `Age`,
`Gender`, `County`, boolean `Died`, etc. The columns are documented on page 12 of this
[FDOH document][def]. Two important columns:

`ChartDate` is the date used to create the bar chart in the FDOH dashboard.

`EventDate` is the date when symptoms started, or if that date is unknown, the
date lab results were reported to the FDOH. One of our sources claim more
precisely this date is the earlier of onset date, diagnosis date, or test date.
Our scripts trust the FDOH and assume `EventDate` is generally the onset date,
but we are aware this column may have data quality issues.

## Forecasting deaths

![Forecast of daily COVID-19 deaths in Florida](forecast_deaths_published.png)

`forecast_deaths.py` does not rely on death data, but relies *solely* on case
ages, date of onset of symptoms, and various estimates of the age-stratified CFR.
The script starts by opening the latest line list CSV file (in directory [data_fdoh](data_fdoh))
or if no such file exists it downloads it from the [FDOH line list page][dataset].
This gives us (1) the age of every case diagnosed with COVID-19, and (2) the
date of onset of symptoms (`EventDate` CSV column.)

The script multiplies the numbers of cases in specific age brackets by the
corresponding age-stratified CFR. The age-stratified CFR estimates are issued
from 5 independent models:

* Model 1: [The Epidemiological Characteristics of an Outbreak of 2019 Novel Coronavirus Diseases (COVID-19) — China, 2020][m1] (table 1, Case fatality rate)
* Model 2: [Estimates of the severity of coronavirus disease 2019: a model-based analysis][m2] (table 1, CFR, Adjusted for censoring, demography, and under-ascertainment)
* Model 3: [https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf][m3] (table 1, Casi totali, % Letalità)
* Model 4: [Case fatality risk by age from COVID-19 in a high testing setting in Latin America: Chile, March-May, 2020][m4] (table 2, Latest estimate)
* Model 5: CFR calculated by the script `age_stratified_cfr.py`

Since the forecast is based on line list case data, ie. *detected* cases, it is
important that we feed it CFR estimates, not IFR estimates. Infection Fatality
Ratios take into account *undetected* cases and thus would not be consistent
with line list data.

Then the script assumes death occurs on average 17.5 days after infection,
which is the mean onset-to-death time calculated by `gamma.py`.

Finally, it charts the forecast (`forecast_deaths.png`). The curves are all
smoothed with a 7-day centered moving average.

The end result is a simple tool that can not only predict deaths up to ~17.5
days ahead of time, but can also estimate *past* deaths accurately: notice how
the colored curves in the generated chart follow closely the black curve
(actual deaths.)

Historical data for actual deaths was fetched from the [New York Times Covid-19
data repository][nyt] and was saved in the file [data_deaths/fl_resident_deaths.csv](data_deaths/fl_resident_deaths.csv).
Death data is only used to draw the black curve. It is *not* used in the
forecasts based on CFR models #1 through #4. Actual deaths are only used
indirectly in the forecast based on model #5, because model #5 uses the
age-stratified CFR calculated from Florida deaths.

Note: since 2020-07-14 the file `data_deaths/fl_resident_deaths.csv` is now
updated by the script [data_fdoh/download](data_fdoh/download) that obtains deaths directly from
the FDOH line list. The number of deaths calculated by the script is off by one
from the "Florida Resident Deaths" figure shown on the [state's
dashboard][dashboard] because my script only accounts for deaths whose `Jurisdiction`
is `FL resident` (consistent with the way NYT does it in their
[repository][nyt],) whereas the state's dashboard includes 1 additional death
whose `Jurisdiction` is `Not diagnosed/isolated in FL`.

## Age-stratified CFR

![CFR of Florida COVID-19 cases by age bracket](age_stratified_cfr_published.png)

`age_stratified_cfr.py` opens the latest line list CSV file (in directory [data_fdoh](data_fdoh))
or if no such file exists it downloads it from the [FDOH line list page][dataset].
It calculates the 7-day moving average of the raw CFR of various age brackets,
with cases ordered by date of onset of symptoms.

The script also calculates the 7-day (short-term) and 28-day (long-term) moving
average of the CFR ajusted for right censoring. The adjustment is performed by
using the parameters of the Gamma distribution of onset-to-death calculated by
`gamma.py`.

The results of these calculations are charted in `age_stratified_cfr.png`.

The short-term adjusted CFR curve helps visualize the magnitude of right censoring:
the curve follows the same peaks and valleys as the raw CFR, but deviates
more greatly toward the right of the time axis, as censoring increases.

The long-term adjusted CFR curve, especially its last value labelled on the chart,
represents our best guess of the age-stratified CFR of COVID-19.

## Gamma distribution of onset-to-death

![Onset-to-death distribution of Florida COVID-19 deaths](gamma_published.png)

`gamma.py` calculates the times between onset of symptoms and death
(onset-to-death) and fits them in a Gamma distribution. It creates
a chart (`gamma.png`) and outputs a numerical summary.

The date of onset is known (`EventDate`). However FDOH does not publish the
date of death, so `gamma.py` infers it from updates made to the line list. We
made daily archives of the line list in directory [data_fdoh](data_fdoh). Pass these files
as arguments to `gamma.py`, it will parse them, and when it detects a new death
(`Died` changed to `Yes`), it infers the date of death was one day before the
line list was updated, because FDOH updates the line list with data as of the
prior day.

```
$ ./gamma.py data_fdoh/*.csv
Parsing data_fdoh/2020-06-27-00-00-00.csv
Parsing data_fdoh/2020-06-28-00-00-00.csv
Parsing data_fdoh/2020-06-29-09-51-00.csv
Parsing data_fdoh/2020-06-30-19-26-00.csv
Parsing data_fdoh/2020-07-01-07-49-00.csv
Parsing data_fdoh/2020-07-02-13-38-00.csv
Parsing data_fdoh/2020-07-03-09-16-00.csv
Parsing data_fdoh/2020-07-04-13-44-00.csv
Parsing data_fdoh/2020-07-05-08-44-00.csv
Parsing data_fdoh/2020-07-06-08-18-00.csv
Parsing data_fdoh/2020-07-07-09-06-00.csv
Parsing data_fdoh/2020-07-08-10-21-00.csv
Parsing data_fdoh/2020-07-09-11-09-00.csv
Parsing data_fdoh/2020-07-10-09-46-54.csv
Parsing data_fdoh/2020-07-11-11-04-49.csv
Parsing data_fdoh/2020-07-12-09-53-27.csv
Parsing data_fdoh/2020-07-13-07-57-16.csv
Parsing data_fdoh/2020-07-14-14-09-16.csv
Parsing data_fdoh/2020-07-15-09-09-26.csv
Parsing data_fdoh/2020-07-16-07-58-41.csv
Parsing data_fdoh/2020-07-17-09-17-34.csv
Parsing data_fdoh/2020-07-18-08-58-55.csv
Onset-to-death times (in days): [16, 7, 27, 20, 29, 32, 22, 15, 26, 31 , 15,
20, 30, 5, 8, 3, 5, 5, 15, 3, 15, 32, 16, 78, 26, 23, 35, 17, 9, 10, 8, 16, 8,
25, 22, 27, 15, 15, 9, 2, 12, 6, 8, 12, 10, 8, 9, 1, 4, 7, 24, 23, 84, 24, 74,
24, 100, 62, 3, 4, 85, 9, 81, 14, 6, 67, 67, 5 4, 19, 20, 54, 17, 5, 64, 4, 2,
35, 28, 8, 39, 31, 22, 28, 23, 16, 28, 16, 32, 8, 8, 19, 21, 9, 16, 12, 7, 10,
7, 6, 16, 5, 11, 6, 6, 7, 6, 4, 8, 12, 3, 3, 7, 2, 7, 4, 2, 10, 24, 7, 1, 81,
88, 24, 61, 29, 59, 5 1, 18, 49, 38, 18, 10, 33, 46, 49, 40, 5, 39, 37, 33, 30,
30, 35, 26, 16, 3, 36, 20, 23, 19, 21, 6, 15, 10, 7, 8, 11, 20, 9, 14, 7, 14,
8, 2 9, 4, 8, 5, 12, 5, 2, 9, 2, 8, 1, 9, 94, 28, 78, 18, 47, 76, 66, 63, 1 0,
42, 21, 10, 58, 10, 19, 55, 7, 55, 47, 66, 19, 21, 40, 9, 40, 30, 2 7, 32, 23,
29, 31, 25, 16, 17, 11, 15, 15, 13, 15, 15, 11, 14, 10, 12, 10, 9, 10, 11, 9,
9, 6, 9, 9, 9, 18, 12, 11, 7, 6, 13, 2, 42, 3, 5, 4 , 1, 12, 2, 5, 33, 11, 9,
9, 5, 53, 11, 9, 5, 12, 35, 23, 9, 1, 5, 13, 6, 53, 10, 49, 49, 27, 19, 53, 41,
31, 26, 23, 23, 28, 15, 35, 41, 46 , 19, 16, 13, 18, 27, 15, 10, 14, 12, 15,
14, 12, 7, 8, 6, 6, 6, 3, 8, 3, 25, 20, 101, 9, 8, 22, 18, 9, 11, 1, 6, 6, 17,
9, 2, 25, 17, 4, 5, 5, 24, 13, 29, 24, 26, 13, 30, 16, 11, 12, 12, 10, 15, 14,
11, 3, 3, 6, 28, 8, 8, 15, 23, 46, 1, 3, 34, 22, 19, 10, 10, 25, 12, 29, 22,
10, 19, 12, 6, 6, 9, 18, 8, 12, 4, 11, 5, 1, 13, 6, 25, 11, 17, 10, 8, 5, 53,
5, 9, 18, 40, 40, 40, 21, 19, 25, 21, 18, 18, 19, 17, 18, 14, 15, 25, 12, 8,
20, 10, 10, 9, 15, 15, 11, 14, 14, 17, 6, 17, 8, 8, 7, 6, 9, 6, 8, 17, 3, 4, 6,
2, 1, 42, 26, 48, 23, 20, 22, 18, 22, 23, 20, 18 , 26, 16, 17, 24, 14, 13, 19,
16, 24, 22, 10, 11, 11, 9, 13, 16, 11, 8 , 13, 10, 17, 15, 30, 10, 87, 73, 12,
61, 42, 15, 3, 10, 9, 8, 15, 8, 8, 15, 11, 11, 6, 5, 9, 4, 4, 8, 13, 10, 10, 9,
3, 3, 7, 2, 9, 8, 12, 52, 16, 29, 27, 29, 31, 26, 20, 16, 18, 15, 14, 13, 24,
12, 4, 2, 9, 1 0, 7, 4, 5, 15, 8, 1, 13, 36, 11, 5, 4, 20, 4, 6, 3, 1, 6, 40,
43, 7, 8, 6, 1, 48, 67, 3, 51, 15, 33, 54, 4, 12, 23, 29, 11, 11, 33, 40, 34,
28, 35, 36, 31, 31, 24, 21, 23, 29, 30, 30, 25, 27, 20, 16, 54, 110, 13, 101,
17, 29, 19, 7, 82, 34, 19, 11, 10, 5, 7, 63, 26, 88, 52, 23, 11, 30, 17, 20,
26, 19, 27, 20, 18, 15, 17, 18, 17, 21, 22, 16, 15, 12 , 13, 15, 14, 18, 13,
14, 14, 12, 17, 17, 18, 13, 14, 14, 19, 10, 9, 1 1, 14, 12, 10, 12, 8, 8, 12,
9, 7, 7, 8, 8, 7, 7, 10, 8, 8, 8, 13, 12, 11, 5, 10, 6, 12, 2, 6, 12, 1, 2, 12,
6, 3, 2, 12, 2, 3, 1, 2, 1, 8, 1, 5, 11, 19, 8, 85, 12, 28, 16, 7, 7, 7, 22, 6,
22, 7, 2, 45, 16, 35, 35, 29, 25, 31, 24, 24, 29, 33, 30, 32, 82, 27, 24, 25,
18, 31, 16, 2 2, 19, 19, 15, 15, 20, 18, 15, 14, 26, 15, 22, 15, 13, 14, 12,
27, 13, 15, 14, 13, 9, 11, 12, 9, 12, 12, 11, 9, 10, 8, 9, 9, 7, 14, 23, 7, 7 ,
10, 14, 11, 5, 9, 15, 6, 6, 5, 18, 5, 3, 4, 6, 9, 4, 3, 2, 8, 8, 20, 3, 10, 10,
11, 20, 1, 19, 16, 2, 20, 91, 54, 55, 6, 30, 6, 10, 9, 62, 13, 40, 9, 21, 3,
50, 44, 34, 37, 35, 25, 30, 50, 34, 24, 31, 27, 21, 26, 63, 26, 28, 29, 31, 23,
27, 32, 20, 21, 30, 21, 21, 19, 19, 22, 2 2, 15, 17, 16, 17, 17, 19, 14, 27,
17, 27, 14, 14, 11, 15, 14, 13, 18, 23, 16, 13, 10, 11, 12, 8, 12, 18, 10, 21,
12, 12, 8, 9, 5, 4, 6, 13, 11, 7, 5, 4, 9, 6, 2, 12, 2, 2, 1, 5, 9, 14, 13, 3,
1, 1, 10, 42, 57, 15, 21, 47, 48, 15, 21, 27, 37, 24, 22, 28, 5, 25, 22, 21,
27, 19, 15 , 18, 23, 16, 13, 12, 11, 14, 16, 12, 13, 11, 12, 12, 7, 9, 5, 7, 7,
7 , 3, 6, 5, 5, 1, 2, 30, 5, 22, 4, 4, 30, 30, 14, 41, 35, 27, 24, 21, 2 3, 18,
19, 18, 19, 16, 30, 18, 20, 18, 14, 17, 12, 10, 12, 10, 7, 14, 2, 10, 9, 7, 10,
9, 18, 5, 93, 23, 14, 24, 81, 6, 11, 16, 2, 41, 5, 10 , 21, 21, 40, 37, 36, 55,
27, 38, 41, 28, 32, 26, 25, 25, 27, 25, 21, 23, 21, 20, 23, 19, 18, 26, 17, 19,
20, 18, 32, 19, 18, 19, 24, 19, 17 , 20, 23, 16, 17, 18, 24, 16, 24, 15, 21,
12, 15, 19, 16, 14, 17, 13, 12, 15, 13, 13, 11, 21, 13, 19, 15, 19, 12, 52, 12,
15, 17, 13, 11, 9, 12, 17, 9, 10, 10, 7, 11, 8, 8, 9, 6, 9, 10, 7, 9, 7, 7, 9,
9, 8, 8, 6, 6, 5, 5, 6, 6, 6, 6, 12, 7, 4, 5, 9, 12, 5, 13, 5, 4, 4, 7, 3, 3,
8, 7, 3, 3, 12, 4, 4, 3, 4, 4, 3, 3, 3, 3, 5, 1, 5, 4, 14, 26, 23, 41, 18, 24,
90, 18, 90, 11, 84, 4, 7, 3
Number of deaths: 1615
Gamma distribution params:
mean = 17.5
shape = 1.72
```

A mean of 17.5 days is comparable to other published estimates, however our
distribution is wider (ie. smaller shape parameter of 1.72) because many deaths
occur in the long tail:
* mean 17.8 days, shape 4.94 = 0.45<sup>-2</sup>, based on sample of 24 deaths: [Estimates of the severity of coronavirus disease 2019: a model-based analysis][verity]
* mean 15.1 days, shape 5.1, based on sample of 3 deaths: [Estimating case fatality ratio of COVID-19 from observed cases outside China][althaus]

We believe our distribution parameters are more accurate because
they are based on a much larger sample of 1615 deaths. The long tail
may be the result of improved treatments that can maintain patients
alive for a longer time.

Limitations: it is likely our technique does not always accurately identify the
date of death. For example FDOH could be updating the line list many days after
the death occured (contributing to the long tail.) Furthermore, there are data
quality issues in the `EventDate` column of the FDOH line list, meaning this
date does not always accurately reflect the date of onset.

## Heatmap of age over time

![Heatmap of COVID-19 cases in Florida](heatmap_published.png)

`heatmap.py` opens the latest line list CSV file (in directory [data_fdoh](data_fdoh))
or if no such file exists it downloads it from the [FDOH line list page][dataset].
It creates the heatmap (`heatmap.png`) of cases by date reported, by age
bracket. The pixel intensity is proportional to the square root of the number
of cases. `heatmap.py` also produces a numerical summary:

```
$ ./heatmap.py
Opening data_fdoh/2020-07-18-08-58-55.csv
Number of COVID-19 cases per 7-day time period in Florida by age bracket over time:
period_start, 00-04, 05-09, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85-89, 90+, median_age
  2020-02-29,     0,     0,     0,     0,     1,     1,     0,     0,     0,     0,     1,     1,     2,     1,     2,     0,     0,     0,     0,  63.0
  2020-03-07,     0,     0,     0,     0,     2,     2,     1,     1,     1,     4,     4,     4,     5,    13,     6,     5,     2,     0,     0,  65.0
  2020-03-14,     0,     2,     0,    18,    40,    36,    34,    28,    30,    50,    40,    43,    48,    57,    31,    32,    19,     7,     8,  53.0
  2020-03-21,     9,     4,    18,    45,   185,   185,   230,   211,   217,   225,   249,   266,   202,   197,   201,   149,   110,    45,    33,  51.0
  2020-03-28,    29,    20,    25,   101,   407,   541,   605,   541,   566,   662,   673,   657,   585,   524,   450,   324,   219,   139,    80,  50.0
  2020-04-04,    31,    22,    37,   111,   387,   494,   612,   567,   594,   671,   718,   700,   629,   585,   420,   327,   271,   167,   138,  51.0
  2020-04-11,    41,    35,    49,   137,   359,   475,   469,   513,   529,   640,   616,   652,   535,   435,   362,   285,   227,   174,   168,  50.0
  2020-04-18,    48,    37,    57,   143,   313,   393,   465,   439,   401,   457,   529,   510,   458,   345,   284,   269,   240,   201,   229,  51.0
  2020-04-25,    29,    36,    57,   118,   274,   322,   329,   374,   312,   370,   399,   405,   325,   307,   249,   209,   197,   191,   179,  51.0
  2020-05-02,    35,    35,    44,   131,   275,   349,   340,   321,   315,   350,   321,   355,   294,   247,   215,   222,   211,   188,   180,  50.0
  2020-05-09,    42,    44,    46,   137,   281,   372,   390,   338,   339,   371,   369,   384,   324,   256,   244,   183,   214,   173,   149,  49.0
  2020-05-16,   102,   100,    97,   204,   362,   434,   472,   485,   413,   478,   424,   443,   348,   280,   229,   219,   183,   178,   171,  46.0
  2020-05-23,    81,    78,   119,   225,   395,   453,   511,   457,   447,   439,   348,   425,   310,   223,   161,   150,   138,   115,    98,  42.0
  2020-05-30,   154,   163,   208,   381,   549,   632,   634,   658,   559,   569,   505,   487,   402,   314,   224,   181,   137,   116,   133,  41.0
  2020-06-06,   238,   213,   261,   543,  1259,  1178,  1079,   959,   762,   810,   761,   683,   552,   387,   300,   225,   201,   163,   173,  38.0
  2020-06-13,   357,   337,   418,  1089,  2842,  2396,  2030,  1712,  1422,  1390,  1250,  1129,   845,   602,   482,   355,   251,   195,   163,  35.0
  2020-06-20,   705,   611,   699,  2587,  6245,  5398,  4445,  3554,  2942,  2884,  2649,  2235,  1629,  1184,   876,   642,   457,   311,   303,  34.0
  2020-06-27,  1017,   954,  1109,  3367,  7156,  6910,  6047,  5127,  4459,  4306,  4154,  3592,  2748,  2004,  1442,  1016,   683,   493,   401,  36.0
  2020-07-04,  1132,  1200,  1474,  3790,  6552,  6769,  6429,  5549,  5048,  5348,  5082,  4572,  3451,  2529,  1890,  1422,   995,   646,   580,  39.0
  2020-07-11,  1305,  1335,  1830,  4692,  8049,  8247,  7931,  7205,  6958,  6860,  6837,  6148,  4714,  3389,  2555,  1880,  1388,   937,   787,  40.0
(Last period's data may be incomplete. Age unknown for 633 out of 337569 cases.)
```

By default the size of each pixel, or *bucket*, is 5-year age brackets and 7-day
time periods. This can be changed by editing the variables `buckets_ages` and `buckets_days`
in `heatmap.py`.

`heatmap.py` also creates `heatmap_age_share.png`: in this version the pixel
intensity represents not the number of cases, but the share of cases in this
age bracket among all cases reported in this time period.

## Miscellaneous

`sort.py` is a tool that strips the `ObjectId` column from a line list CSV file
and sorts the rows. This is helpful to compare 2 CSV files published on 2
different days, because the `ObjectId` value and the order of rows are not
stable from one file to another.

[dataset]: https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
[def]: https://justthenews.com/sites/default/files/2020-07/Data_Definitions_05182020-2.pdf
[m1]: http://weekly.chinacdc.cn/en/article/doi/10.46234/ccdcw2020.032
[m2]: https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30243-7/fulltext
[m3]: https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf
[m4]: https://www.medrxiv.org/content/10.1101/2020.05.25.20112904v1
[nyt]: https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv
[dashboard]: https://experience.arcgis.com/experience/96dd742462124fa0b38ddedb9b25e429
[verity]: https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30243-7/fulltext
[althaus]: https://github.com/calthaus/ncov-cfr/
