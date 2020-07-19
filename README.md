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

Overall distribution (all ages):

![Onset-to-death distribution of Florida COVID-19 deaths, all ages](gamma_0-inf_published.png)

Distribution by age bracket:

![Onset-to-death distribution of Florida COVID-19 deaths, ages 0-29](gamma_0-29_published.png)

![Onset-to-death distribution of Florida COVID-19 deaths, ages 30-39](gamma_30-39_published.png)

![Onset-to-death distribution of Florida COVID-19 deaths, ages 40-49](gamma_40-49_published.png)

![Onset-to-death distribution of Florida COVID-19 deaths, ages 50-59](gamma_50-59_published.png)

![Onset-to-death distribution of Florida COVID-19 deaths, ages 60-69](gamma_60-69_published.png)

![Onset-to-death distribution of Florida COVID-19 deaths, ages 70-79](gamma_70-79_published.png)

![Onset-to-death distribution of Florida COVID-19 deaths, ages 80-89](gamma_80-89_published.png)

![Onset-to-death distribution of Florida COVID-19 deaths, ages 90+](gamma_90-inf_published.png)

`gamma.py` calculates the times between onset of symptoms and death
(onset-to-death) and fits them in a Gamma distribution. It creates
multiple charts for different age brackets (`gamma*.png`) and outputs a
numerical summary.

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

Ages 0-29:
Number of deaths: 17
Gamma distribution params:
mean = 12.9
shape = 2.84

Ages 30-39:
Number of deaths: 37
Gamma distribution params:
mean = 17.0
shape = 1.26

Ages 40-49:
Number of deaths: 57
Gamma distribution params:
mean = 20.3
shape = 1.94

Ages 50-59:
Number of deaths: 118
Gamma distribution params:
mean = 19.8
shape = 1.54

Ages 60-69:
Number of deaths: 250
Gamma distribution params:
mean = 18.5
shape = 1.82

Ages 70-79:
Number of deaths: 397
Gamma distribution params:
mean = 18.8
shape = 1.63

Ages 80-89:
Number of deaths: 462
Gamma distribution params:
mean = 16.7
shape = 1.86

Ages 90+:
Number of deaths: 277
Gamma distribution params:
mean = 15.1
shape = 1.75

All ages:
Number of deaths: 1615
Gamma distribution params:
mean = 17.5
shape = 1.72
```

The overall (all ages) mean of 17.5 days is comparable to other published estimates, however our
distribution is wider (ie. smaller shape parameter of 1.72) because many deaths
occur in the long tail:
* mean 17.8 days, shape 4.94 = 0.45<sup>-2</sup>, based on sample of 24 deaths: [Estimates of the severity of coronavirus disease 2019: a model-based analysis][verity]
* mean 15.1 days, shape 5.1, based on sample of 3 deaths: [Estimating case fatality ratio of COVID-19 from observed cases outside China][althaus]

We believe our distribution parameters are more accurate because
they are based on a much larger sample of 1615 deaths. The long tail
may be the result of improved treatments that can maintain patients
alive for a longer time.

We notice differences between age brackets. For example patients aged 0-29
years have the shortest onset-to-death time (mean of 12.9 days.) However
for the purpose of calculating the age-stratified CFR (`age_stratified_cfr.py`)
and forecasting deaths (`forecast_deaths.py`) we do not use age-specific
Gamma parameters. Instead we simply use the parameters of the overall distribution
(all ages.)

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
