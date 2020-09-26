# Forecasting deaths and analyzing age trends of COVID-19 cases in Florida

*Updated: 25 September 2020*

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
It calculates the 7-day moving average of the raw CFR of various age brackets,
with cases ordered by date of onset of symptoms.

The script also calculates the 7-day (short-term) and 21-day (long-term) moving
average of the CFR ajusted for right censoring. The adjustment is performed by
using the parameters of the Gamma distribution of onset-to-death calculated by
`gamma.py`. The long-term average is calculated over 21 days shifted by 7 days
(days D-7 through D-27) because despite best efforts to adjust for censoring,
the number of deaths in the last 7 days still remains too incomplete to make the
adjustment accurate (garbage in, garbage out.)

All the moving averages are calculated by assigning equal *weight* to each
day's CFR value. If they were calculated by summing all cases and deaths across
the entire 7-day or 21-day period, this would give too much weight to days
with more cases and would not be representative of the overall average over
the entire 7 or 21 days.

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
Opening data_fdoh/2020-09-25-07-58-17.csv
Number of COVID-19 cases per 7-day time period in Florida by age bracket over time:
period_start, 00-04, 05-09, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85+, median_age
  2020-02-28,     0,     0,     0,     0,     1,     1,     0,     0,     0,     0,     1,     1,     2,     1,     2,     0,     0,     0,  63.0
  2020-03-06,     0,     0,     0,     0,     0,     0,     0,     0,     0,     1,     1,     3,     5,    10,     2,     3,     1,     0,  66.5
  2020-03-13,     0,     1,     0,    15,    33,    27,    25,    23,    26,    38,    31,    32,    33,    41,    24,    26,    11,    11,  51.0
  2020-03-20,     9,     4,    17,    42,   149,   159,   181,   161,   165,   200,   193,   203,   166,   169,   152,   129,    88,    55,  50.0
  2020-03-27,    24,    18,    18,    87,   382,   475,   550,   515,   528,   590,   614,   621,   519,   467,   434,   287,   202,   196,  50.0
  2020-04-03,    32,    22,    41,   108,   388,   533,   646,   578,   610,   680,   736,   700,   648,   605,   430,   345,   279,   294,  51.0
  2020-04-10,    37,    34,    44,   132,   365,   451,   468,   489,   525,   644,   618,   663,   558,   464,   379,   280,   230,   346,  51.0
  2020-04-17,    45,    35,    59,   148,   321,   417,   483,   471,   426,   498,   566,   547,   483,   359,   301,   287,   252,   450,  51.0
  2020-04-24,    35,    36,    55,   119,   285,   337,   342,   389,   331,   371,   409,   407,   328,   294,   231,   207,   186,   362,  50.0
  2020-05-01,    33,    34,    44,   135,   257,   328,   303,   306,   288,   343,   334,   341,   285,   261,   231,   228,   219,   374,  51.0
  2020-05-08,    42,    47,    46,   142,   318,   414,   447,   357,   374,   410,   383,   406,   337,   270,   246,   191,   212,   314,  48.0
  2020-05-15,    93,    90,    95,   182,   339,   414,   442,   471,   379,   439,   399,   436,   350,   260,   239,   198,   192,   354,  47.0
  2020-05-22,    80,    79,   111,   222,   391,   439,   501,   449,   445,   442,   362,   412,   300,   244,   158,   158,   139,   219,  43.0
  2020-05-29,   121,   147,   183,   339,   488,   566,   598,   591,   528,   531,   458,   481,   398,   300,   208,   191,   137,   246,  42.0
  2020-06-05,   235,   202,   248,   493,  1076,  1027,   916,   842,   676,   721,   663,   597,   485,   338,   281,   188,   177,   300,  38.0
  2020-06-12,   337,   313,   377,   956,  2471,  2126,  1881,  1603,  1311,  1295,  1198,  1062,   804,   566,   458,   343,   250,   361,  36.0
  2020-06-19,   598,   530,   641,  2225,  5504,  4638,  3808,  2997,  2510,  2465,  2245,  1905,  1389,  1012,   763,   564,   393,   549,  34.0
  2020-06-26,  1028,   928,  1033,  3296,  6961,  6773,  5791,  4993,  4252,  4096,  3944,  3357,  2635,  1926,  1406,   967,   683,   907,  36.0
  2020-07-03,  1110,  1172,  1451,  3836,  7115,  7108,  6656,  5667,  5119,  5320,  5065,  4556,  3348,  2441,  1810,  1367,   908,  1123,  38.0
  2020-07-10,  1289,  1318,  1821,  4669,  8063,  8320,  7988,  7156,  6862,  6823,  6720,  6041,  4674,  3324,  2479,  1811,  1366,  1634,  40.0
  2020-07-17,  1432,  1394,  2081,  4294,  6471,  6518,  6755,  6361,  6108,  6285,  6075,  5564,  4453,  3430,  2523,  1925,  1375,  1797,  41.0
  2020-07-24,  1217,  1336,  1720,  3729,  5582,  5816,  6228,  5944,  5448,  5794,  5700,  5361,  4018,  3013,  2228,  1680,  1276,  1602,  42.0
  2020-07-31,   826,   964,  1360,  2523,  3759,  3985,  4152,  4105,  3842,  3986,  3940,  3805,  2995,  2223,  1663,  1242,   937,  1306,  42.0
  2020-08-07,   748,   898,  1241,  2500,  3654,  3776,  3933,  3873,  3684,  3788,  3757,  3558,  2785,  1992,  1593,  1143,   869,  1259,  42.0
  2020-08-14,   642,   705,   982,  1648,  2242,  2436,  2422,  2464,  2267,  2388,  2391,  2349,  1893,  1450,  1197,   908,   719,   972,  43.0
  2020-08-21,   432,   543,   700,  1376,  1832,  1739,  1826,  1716,  1647,  1790,  1797,  1725,  1409,  1114,   866,   702,   530,   699,  43.0
  2020-08-28,   436,   545,   704,  1978,  2619,  1930,  1833,  1851,  1697,  1804,  1851,  1705,  1453,  1134,   915,   715,   539,   772,  40.0
  2020-09-04,   349,   431,   512,  2517,  2371,  1231,  1265,  1164,  1145,  1162,  1209,  1179,  1067,   800,   686,   505,   424,   583,  37.0
  2020-09-11,   336,   374,   543,  2460,  2687,  1364,  1377,  1276,  1227,  1310,  1270,  1227,  1047,   836,   680,   537,   398,   560,  37.0
  2020-09-18,   303,   378,   553,  1945,  2259,  1456,  1340,  1294,  1212,  1294,  1269,  1298,  1032,   780,   690,   538,   413,   446,  38.0
(Last period's data may be incomplete. Age unknown for 1854 out of 695887 cases.)
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
