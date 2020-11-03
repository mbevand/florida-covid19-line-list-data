# Forecasting deaths and analyzing age trends of COVID-19 cases in Florida

*Updated: 03 Nov 2020*

Author: Marc Bevand

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
`Download` in the top right corner. However we already made daily archives of the line
list in directory [data_fdoh](data_fdoh) so there is no need to download it.

The line list is in CSV format and the columns are self-explanatory: `Age`,
`Gender`, `County`, boolean `Died`, etc. The columns are documented on page 12 of this
[FDOH document][def]. Two important columns:

`ChartDate` is the date used to create the bar chart in the FDOH [dashboard][dashboard].

`EventDate` is the date when symptoms started, or if that date is unknown, the
date lab results were reported to the FDOH. One of our sources claim more
precisely this date is the earlier of onset date, diagnosis date, or test date.
Our scripts trust the FDOH and assume `EventDate` is generally the onset date,
but we are aware this column may have data quality issues.

## Forecasting deaths

### Previous forecasts

List of our previous forecasts ([directory](historical)):

* [2020-07-05 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-07-05.png), first published [here](https://twitter.com/zorinaq/status/1279934357323386880)
* [2020-07-11 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-07-11.png), first published [here](https://twitter.com/zorinaq/status/1282184250163224576)
* [2020-07-14 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-07-14.png), first published [here](https://twitter.com/zorinaq/status/1283195508777824256)
* [2020-07-18 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-07-18.png), first published [here](https://twitter.com/zorinaq/status/1284544737110683648)
* [2020-07-22 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-07-22.png), first published [here](https://twitter.com/zorinaq/status/1286054539003482114)
* [2020-07-26 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-07-26.png), first published [here](https://twitter.com/zorinaq/status/1287650007340822528)
* [2020-07-30 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-07-30.png), first published [here](https://twitter.com/zorinaq/status/1288951536299565056)
* [2020-08-03 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-08-03.png), first published [here](https://twitter.com/zorinaq/status/1290500240454254597)
* [2020-08-07 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-08-07.png), first published [here](https://twitter.com/zorinaq/status/1291974213880827905)
* [2020-08-11 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-08-11.png), first published [here](https://twitter.com/zorinaq/status/1293435528210034690)
* [2020-08-16 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-08-16.png), first published [here](https://twitter.com/zorinaq/status/1295235407030829059)
* [2020-08-21 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-08-21.png), first published [here](https://twitter.com/zorinaq/status/1296897188136497155)
* [2020-08-27 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-08-27.png), first published [here](https://twitter.com/zorinaq/status/1299127359589605376)
* [2020-09-01 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-09-01.png), first published [here](https://twitter.com/zorinaq/status/1300952032023425026)
* [2020-09-09 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-09-09.png), first published [here](https://twitter.com/zorinaq/status/1303748003027582976)
* [2020-09-19 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-09-19.png), first published [here](https://twitter.com/zorinaq/status/1307548097698914306)
* [2020-10-03 forecast](https://raw.githubusercontent.com/mbevand/florida-covid19-line-list-data/master/historical/forecast_deaths_2020-10-03.png), first published [here](https://twitter.com/zorinaq/status/1312512597795590144)

### Most recent forecast

![Forecast of daily COVID-19 deaths in Florida](forecast_deaths_published.png)

Our previous forecasts have been accurate, for example our first forecasts
accurately predicted the increase of deaths in July:

![Forecast of daily COVID-19 deaths in Florida](historical/forecast_deaths_2020-07-05.png)

`forecast_deaths.py` does not rely on death data, but relies *solely* on case
ages, date of onset of symptoms, and various estimates of the age-stratified CFR.
The script starts by opening the latest line list CSV file (in directory [data_fdoh](data_fdoh))
or if no such file exists it downloads it from the [FDOH line list page][dataset].
This gives us (1) the age of every case diagnosed with COVID-19, and (2) the
date of onset of symptoms (`EventDate` CSV column.)

The script multiplies the numbers of cases in specific age brackets by the
corresponding age-stratified CFR. The age-stratified CFR estimates are issued
from multiple independent models:

* Model 2: [Estimates of the severity of coronavirus disease 2019: a model-based analysis][m2] (table 1, CFR, Adjusted for censoring, demography, and under-ascertainment)
* Model 4: [Case fatality risk by age from COVID-19 in a high testing setting in Latin America: Chile, March-May, 2020][m4] (table 2, Latest estimate)
* Model 5: CFR calculated on the Florida line list by the script `age_stratified_cfr.py`

Model 1 was removed on 2020-07-26 as it is based on the same case data as model 2 but without adjustments for censoring and under-ascertainment:
* Model 1: [The Epidemiological Characteristics of an Outbreak of 2019 Novel Coronavirus Diseases (COVID-19) — China, 2020][m1] (table 1, Case fatality rate)

Model 3 was removed on 2020-07-26 as it did not prove to be as reliable as the others:
* Model 3: [https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf][m3] (table 1, Casi totali, % Letalità)

Experimentally, we have observed that deaths fall somewhere in the range of
estimates produced by these CFR models (eg. model 4 tends to overestimate, and
model 5 tends to underestimate.) To refine our estimates, since 2020-07-26
we also produce a *best guess forecast*:

* We assume the rate of increase/decrease of daily deaths is most closely
  forecast by model 5
* We calculate a factor `adj_factor` by which model 5 estimates can be multiplied
  to produce a perfect estimate for the present day
* For our best guess upper bound: the next day, `adj_factor` is multiplied by 1.05
  (5% error margin), for every subsequent day `adj_factor` is multiplied by 1.005
  (accumulates 0.5% daily error margin)
* For our best guess lower bound: same, but with 0.95, and 0.995

Since the forecast is based on line list case data, ie. *detected* cases, it is
important that we feed it CFR estimates, not IFR estimates. Infection Fatality
Ratios take into account *undetected* cases and thus would not be consistent
with line list data.

Then the script assumes death occurs on average 25.1 days after infection,
which is the mean onset-to-death time calculated by `gamma.py`.

Finally, it charts the forecast (`forecast_deaths.png`). The curves are all
smoothed with a 7-day simple moving average.

The end result is a simple tool that can not only predict deaths up to ~25.1
days ahead of time, but can also estimate *past* deaths accurately: notice how
the colored curves in the generated chart follow closely the observed deaths.

Historical data for observed deaths was fetched from the [New York Times Covid-19
data repository][nyt] and was saved in the file [data_deaths/fl_resident_deaths.csv](data_deaths/fl_resident_deaths.csv).
Death data is only used to draw the black curve. It is *not* used in the
forecasts based on CFR models #1 through #4. Actual deaths are only used
indirectly in the forecast based on model #5, because model #5 uses the
age-stratified CFR calculated from Florida deaths.

Note: since 2020-07-14 the file `data_deaths/fl_resident_deaths.csv` is now
updated by the script [data_fdoh/download](data_fdoh/download) that obtains deaths directly from
the FDOH line list. The number of deaths calculated by the script is off by one
from the "Florida Resident Deaths" figure shown on the [state's
dashboard][dashboard] because our script only accounts for deaths whose `Jurisdiction`
is `FL resident` (consistent with the way NYT does it in their
[repository][nyt],) whereas the state's dashboard includes 1 additional death
whose `Jurisdiction` is `Not diagnosed/isolated in FL`.

## Age-stratified CFR

![CFR of Florida COVID-19 cases by age bracket](age_stratified_cfr_published.png)

`age_stratified_cfr.py` opens the latest line list CSV file (in directory [data_fdoh](data_fdoh))
or if no such file exists it downloads it from the [FDOH line list page][dataset].
It calculates the 14-day moving average of the raw CFR of various age brackets,
with cases ordered by date of onset of symptoms.

The script also calculates the 14-day (short-term) and 35-day (long-term) moving
average of the CFR ajusted for right censoring. The adjustment is performed by
using the parameters of the Gamma distribution of onset-to-death calculated by
`gamma.py`. The long-term average is calculated over 35 days shifted by 14 days
(days D-14 through D-48) because despite best efforts to adjust for censoring,
the number of deaths in the last 14 days still remains too incomplete to make the
adjustment accurate (garbage in, garbage out.)

All the moving averages are calculated by assigning equal *weight* to each
day's CFR value. If they were calculated by summing all cases and deaths across
the entire 14-day or 35-day period, this would give too much weight to days
with more cases and would not be representative of the overall average over
the entire 14 or 35 days.

The results of these CFR calculations are charted in `age_stratified_cfr.png`.

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
Parsing data_fdoh/2020-07-19-10-12-32.csv
Parsing data_fdoh/2020-07-20-08-30-29.csv
Parsing data_fdoh/2020-07-21-09-22-37.csv
Parsing data_fdoh/2020-07-22-08-26-38.csv
Parsing data_fdoh/2020-07-23-09-44-13.csv
Parsing data_fdoh/2020-07-24-09-32-33.csv
Parsing data_fdoh/2020-07-25-07-38-52.csv
Parsing data_fdoh/2020-07-26-08-01-29.csv
Parsing data_fdoh/2020-07-27-11-17-26.csv
Parsing data_fdoh/2020-07-28-09-08-33.csv
Parsing data_fdoh/2020-07-29-11-28-29.csv
Parsing data_fdoh/2020-07-30-12-31-00.csv
Parsing data_fdoh/2020-07-31-07-45-07.csv
Parsing data_fdoh/2020-08-01-07-45-35.csv
Parsing data_fdoh/2020-08-02-07-44-56.csv
Parsing data_fdoh/2020-08-03-07-38-28.csv
Parsing data_fdoh/2020-08-04-07-57-47.csv
Parsing data_fdoh/2020-08-05-08-38-43.csv
Parsing data_fdoh/2020-08-06-08-29-41.csv
Parsing data_fdoh/2020-08-07-07-57-53.csv
Parsing data_fdoh/2020-08-08-07-54-58.csv
Parsing data_fdoh/2020-08-09-07-39-31.csv
Parsing data_fdoh/2020-08-10-07-53-43.csv
Parsing data_fdoh/2020-08-11-08-01-22.csv
Parsing data_fdoh/2020-08-12-07-52-36.csv
Parsing data_fdoh/2020-08-13-09-40-37.csv
Parsing data_fdoh/2020-08-14-13-14-28.csv
Parsing data_fdoh/2020-08-15-08-01-33.csv
Parsing data_fdoh/2020-08-16-07-41-33.csv
Parsing data_fdoh/2020-08-17-15-00-53.csv
Parsing data_fdoh/2020-08-18-07-42-14.csv
Parsing data_fdoh/2020-08-19-08-02-46.csv
Parsing data_fdoh/2020-08-20-07-53-41.csv
Parsing data_fdoh/2020-08-21-08-06-24.csv
Parsing data_fdoh/2020-08-22-07-43-00.csv
Parsing data_fdoh/2020-08-23-07-55-32.csv
Parsing data_fdoh/2020-08-24-08-00-18.csv
Parsing data_fdoh/2020-08-25-07-53-22.csv
Parsing data_fdoh/2020-08-26-07-53-06.csv
Parsing data_fdoh/2020-08-27-07-50-53.csv
Parsing data_fdoh/2020-08-28-07-43-14.csv
Parsing data_fdoh/2020-08-29-08-08-09.csv
Parsing data_fdoh/2020-08-30-09-58-03.csv
Parsing data_fdoh/2020-08-31-07-43-19.csv
Parsing data_fdoh/2020-09-01-10-43-29.csv
Parsing data_fdoh/2020-09-02-08-04-15.csv
Parsing data_fdoh/2020-09-03-08-08-03.csv
Parsing data_fdoh/2020-09-04-09-08-26.csv
Parsing data_fdoh/2020-09-05-08-02-30.csv
Parsing data_fdoh/2020-09-06-08-48-47.csv
Parsing data_fdoh/2020-09-07-10-23-19.csv
Parsing data_fdoh/2020-09-08-07-51-31.csv
Parsing data_fdoh/2020-09-09-08-02-46.csv

Ages 0-29:
Number of deaths: 59
Gamma distribution params:
mean = 19.8
shape = 1.51
Median: 14.0

Ages 30-39:
Number of deaths: 107
Gamma distribution params:
mean = 22.5
shape = 1.35
Median: 19.0

Ages 40-49:
Number of deaths: 275
Gamma distribution params:
mean = 28.6
shape = 1.99
Median: 23.0

Ages 50-59:
Number of deaths: 698
Gamma distribution params:
mean = 28.0
shape = 2.00
Median: 24.5

Ages 60-69:
Number of deaths: 1562
Gamma distribution params:
mean = 27.1
shape = 2.17
Median: 24.0

Ages 70-79:
Number of deaths: 2508
Gamma distribution params:
mean = 25.3
shape = 2.10
Median: 22.0

Ages 80-89:
Number of deaths: 2814
Gamma distribution params:
mean = 24.1
shape = 1.93
Median: 19.0

Ages 90+:
Number of deaths: 1549
Gamma distribution params:
mean = 22.8
shape = 1.80
Median: 19.0

All ages:
Number of deaths: 9572
Gamma distribution params:
mean = 25.1
shape = 1.97
Median: 21.0
```

The overall (all ages) mean of 25.1 days is comparable to other published estimates, however our
distribution is wider (ie. smaller shape parameter of 1.97) because many deaths
occur in the long tail:
* mean 17.8 days, shape 4.94 = 0.45<sup>-2</sup>, based on sample of 24 deaths: [Estimates of the severity of coronavirus disease 2019: a model-based analysis][verity]
* mean 15.1 days, shape 5.1, based on sample of 3 deaths: [Estimating case fatality ratio of COVID-19 from observed cases outside China][althaus]

We believe our distribution parameters are more accurate because
they are based on a much larger sample of 9572 deaths. The long tail
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

![Heatmap of COVID-19 cases in Florida (per capita)](heatmap_per_capita_published.png)

![Heatmap of COVID-19 cases in Florida (percentage)](heatmap_age_share_published.png)

`heatmap.py` opens the latest line list CSV file (in directory [data_fdoh](data_fdoh))
or if no such file exists it downloads it from the [FDOH line list page][dataset].
It creates various heatmaps of cases by age over time:

* In `heatmap.png` the pixel intensity represents the number of cases
* In `heatmap_per_capita.png` the pixel intensity represents the number of cases per capita
* In `heatmap_age_share.png` the pixel intensity represents the percentage of cases in the age bracket among all cases in this time period

`heatmap.py` also produces a numerical summary:

```
$ ./heatmap.py
Opening data_fdoh/2020-11-02-10-03-30.csv.gz
Number of COVID-19 cases per 7-day time period in Florida by age bracket over time:
period_start, 00-04, 05-09, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85+, median_age
  2020-03-02,     0,     0,     0,     0,     1,     1,     0,     0,     0,     0,     1,     1,     2,     3,     2,     3,     0,     0,  65.5
  2020-03-09,     0,     0,     0,     8,     9,     6,     3,     7,     8,    10,     5,    10,    13,    21,    11,     6,     4,     2,  57.0
  2020-03-16,     0,     2,     5,    22,    74,    63,    80,    55,    62,    83,    84,    90,    78,    87,    52,    60,    42,    29,  52.0
  2020-03-23,    13,     8,    15,    55,   240,   284,   323,   306,   318,   341,   373,   355,   283,   268,   262,   194,   146,   108,  50.0
  2020-03-30,    37,    18,    32,   107,   419,   548,   641,   572,   583,   669,   706,   701,   616,   572,   484,   334,   222,   226,  50.0
  2020-04-06,    29,    31,    49,   116,   391,   496,   560,   539,   581,   699,   697,   699,   635,   563,   407,   323,   266,   339,  51.0
  2020-04-13,    36,    31,    36,   139,   314,   434,   474,   497,   477,   572,   582,   591,   494,   383,   341,   273,   228,   346,  50.0
  2020-04-20,    51,    41,    68,   155,   337,   395,   427,   449,   407,   457,   497,   491,   416,   327,   261,   243,   227,   427,  50.0
  2020-04-27,    31,    35,    52,   112,   264,   337,   330,   349,   327,   366,   391,   395,   355,   319,   248,   247,   219,   381,  52.0
  2020-05-04,    31,    31,    36,   117,   243,   314,   329,   296,   281,   328,   296,   343,   266,   227,   204,   188,   188,   352,  50.0
  2020-05-11,    59,    65,    66,   168,   346,   437,   453,   429,   370,   405,   431,   441,   377,   277,   267,   189,   225,   343,  48.0
  2020-05-18,   100,    95,   114,   217,   386,   419,   465,   447,   431,   472,   377,   411,   307,   274,   192,   194,   163,   292,  45.0
  2020-05-25,    84,    94,   128,   224,   387,   454,   505,   459,   440,   430,   358,   429,   313,   229,   172,   164,   130,   201,  42.0
  2020-06-01,   190,   172,   210,   424,   676,   764,   719,   720,   589,   626,   589,   547,   425,   326,   244,   193,   152,   282,  40.0
  2020-06-08,   259,   269,   305,   625,  1535,  1370,  1249,  1101,   900,   909,   847,   720,   590,   429,   331,   233,   208,   315,  37.0
  2020-06-15,   413,   349,   452,  1361,  3492,  2916,  2434,  1997,  1643,  1623,  1446,  1334,   962,   671,   546,   399,   275,   406,  34.0
  2020-06-22,   806,   698,   803,  2875,  6866,  6145,  5035,  4162,  3494,  3379,  3146,  2623,  2006,  1469,  1064,   757,   527,   762,  35.0
  2020-06-29,  1086,  1071,  1248,  3541,  7094,  6970,  6337,  5373,  4637,  4559,  4377,  3841,  2867,  2079,  1500,  1089,   699,   819,  36.0
  2020-07-06,  1172,  1245,  1632,  4357,  7693,  7822,  7521,  6462,  6140,  6276,  6027,  5492,  4174,  2952,  2178,  1613,  1179,  1486,  39.0
  2020-07-13,  1371,  1380,  1928,  4467,  7014,  7287,  7164,  6633,  6367,  6430,  6349,  5731,  4490,  3383,  2569,  1913,  1395,  1719,  41.0
  2020-07-20,  1375,  1404,  1979,  3997,  6047,  6193,  6485,  6143,  5810,  6121,  5999,  5410,  4318,  3199,  2384,  1826,  1384,  1762,  41.0
  2020-07-27,  1046,  1189,  1599,  3275,  4853,  4968,  5270,  5127,  4667,  5005,  4839,  4793,  3562,  2700,  1995,  1472,  1140,  1439,  42.0
  2020-08-03,   756,   910,  1222,  2359,  3517,  3830,  3977,  3992,  3716,  3734,  3702,  3472,  2854,  2111,  1541,  1152,   825,  1212,  42.0
  2020-08-10,   706,   804,  1168,  2185,  3132,  3178,  3279,  3247,  3129,  3211,  3282,  3097,  2362,  1773,  1486,  1099,   846,  1242,  43.0
  2020-08-17,   528,   590,   808,  1453,  2057,  2198,  2236,  2191,  2020,  2182,  2132,  2125,  1700,  1317,  1016,   787,   635,   786,  43.0
  2020-08-24,   402,   480,   642,  1350,  1703,  1568,  1529,  1526,  1465,  1576,  1642,  1500,  1284,  1012,   850,   675,   502,   724,  43.0
  2020-08-31,   432,   554,   664,  2668,  3049,  1908,  1883,  1768,  1642,  1763,  1789,  1652,  1435,  1090,   888,   649,   498,   747,  38.0
  2020-09-07,   322,   426,   517,  2333,  2378,  1192,  1201,  1178,  1122,  1138,  1152,  1122,  1020,   769,   641,   492,   387,   502,  37.0
  2020-09-14,   320,   341,   545,  2347,  2696,  1499,  1458,  1303,  1307,  1348,  1316,  1295,  1043,   827,   701,   550,   451,   556,  37.0
  2020-09-21,   284,   366,   547,  1566,  1818,  1238,  1167,  1139,  1019,  1145,  1142,  1185,   963,   700,   629,   477,   325,   367,  39.0
  2020-09-28,   307,   392,   538,  1424,  1683,  1338,  1347,  1281,  1208,  1274,  1246,  1139,  1028,   821,   732,   510,   352,   416,  40.0
  2020-10-05,   295,   430,   668,  1520,  1891,  1561,  1469,  1384,  1252,  1321,  1286,  1215,  1074,   881,   743,   532,   370,   376,  39.0
  2020-10-12,   265,   447,   690,  1948,  2419,  1827,  1605,  1522,  1349,  1525,  1531,  1480,  1194,   955,   818,   530,   325,   383,  38.0
  2020-10-19,   354,   561,   861,  2183,  2925,  2457,  2098,  1889,  1728,  1771,  1790,  1777,  1412,  1150,   904,   682,   410,   481,  38.0
  2020-10-26,   497,   728,  1072,  2126,  3068,  2829,  2530,  2326,  2149,  2202,  2295,  2240,  1790,  1413,  1176,   822,   487,   527,  39.0
(Last period's data may be incomplete. Age unknown for 1073 out of 812063 cases.)
```

By default the size of each pixel, or *bucket*, is 5-year age brackets and 7-day
time periods. This can be changed by editing the variables `buckets_ages` and `buckets_days`
in `heatmap.py`.

## Miscellaneous

`sort.py` is a tool that strips the `ObjectId` column from a line list CSV file
and sorts the rows. This is helpful to compare 2 CSV files published on 2
different days, because the `ObjectId` value and the order of rows are not
stable from one file to another.

## Other COVID-19 line lists

* [Ohio](https://coronavirus.ohio.gov/wps/portal/gov/covid-19/dashboards/overview) (click *Download the summary data (CSV)*)
* [Virginia](https://www.vdh.virginia.gov/coronavirus/)
* [Tokyo](https://twitter.com/sugi2000/status/1285325952981983232)

[dataset]: https://www.arcgis.com/home/item.html?id=4cc62b3a510949c7a8167f6baa3e069d
[def]: https://justthenews.com/sites/default/files/2020-07/Data_Definitions_05182020-2.pdf
[m1]: http://weekly.chinacdc.cn/en/article/doi/10.46234/ccdcw2020.032
[m2]: https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30243-7/fulltext
[m3]: https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_26-marzo%202020.pdf
[m4]: https://www.medrxiv.org/content/10.1101/2020.05.25.20112904v1
[nyt]: https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv
[dashboard]: https://experience.arcgis.com/experience/96dd742462124fa0b38ddedb9b25e429
[verity]: https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30243-7/fulltext
[althaus]: https://github.com/calthaus/ncov-cfr/
