# Forecasting deaths and analyzing age trends of COVID-19 cases in Florida

*Updated: 27 Sep 2020*

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
Opening data_fdoh/2020-09-27-08-09-26.csv
Number of COVID-19 cases per 7-day time period in Florida by age bracket over time:
period_start, 00-04, 05-09, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85+, median_age
  2020-03-01,     0,     0,     0,     0,     1,     1,     0,     0,     0,     0,     1,     1,     2,     2,     2,     3,     0,     0,  65.0
  2020-03-08,     0,     0,     0,     4,     7,     3,     2,     5,     6,     8,     4,     8,     9,    17,    10,     4,     3,     1,  59.0
  2020-03-15,     0,     2,     3,    21,    57,    48,    45,    36,    34,    63,    54,    64,    64,    67,    40,    41,    30,    26,  53.0
  2020-03-22,    10,     5,    17,    49,   205,   223,   282,   254,   272,   273,   315,   298,   235,   235,   237,   176,   121,    84,  50.0
  2020-03-29,    32,    21,    28,   109,   428,   577,   652,   583,   604,   701,   716,   704,   631,   550,   470,   345,   234,   228,  50.0
  2020-04-05,    34,    25,    42,   108,   383,   481,   569,   541,   577,   669,   699,   706,   636,   593,   418,   313,   262,   326,  51.0
  2020-04-12,    37,    35,    41,   142,   330,   437,   465,   494,   490,   608,   595,   613,   493,   405,   335,   270,   220,   344,  50.0
  2020-04-19,    49,    39,    67,   149,   341,   427,   459,   466,   416,   462,   518,   498,   441,   332,   279,   259,   246,   424,  50.0
  2020-04-26,    29,    29,    55,   111,   251,   296,   308,   339,   305,   348,   375,   382,   323,   301,   240,   235,   205,   382,  52.0
  2020-05-03,    37,    38,    35,   132,   276,   364,   355,   321,   319,   364,   328,   373,   297,   245,   225,   212,   202,   363,  50.0
  2020-05-10,    51,    58,    60,   151,   313,   401,   435,   399,   354,   399,   424,   432,   351,   270,   262,   191,   225,   334,  49.0
  2020-05-17,    94,    88,    98,   193,   329,   392,   423,   417,   392,   443,   357,   379,   306,   257,   197,   188,   161,   312,  46.0
  2020-05-24,    91,    94,   136,   242,   425,   481,   544,   491,   468,   447,   375,   444,   336,   237,   165,   159,   144,   207,  42.0
  2020-05-31,   162,   161,   201,   400,   624,   707,   693,   706,   594,   617,   560,   540,   413,   333,   232,   181,   138,   270,  40.0
  2020-06-07,   258,   256,   290,   592,  1399,  1287,  1151,  1019,   813,   840,   806,   688,   575,   403,   320,   235,   205,   324,  37.0
  2020-06-14,   392,   342,   436,  1272,  3356,  2757,  2317,  1940,  1606,  1554,  1364,  1277,   915,   650,   529,   378,   271,   379,  34.0
  2020-06-21,   765,   643,   762,  2757,  6592,  5829,  4807,  3907,  3229,  3193,  2943,  2437,  1868,  1349,   990,   718,   496,   722,  34.0
  2020-06-28,  1069,  1047,  1203,  3467,  7124,  6986,  6220,  5293,  4588,  4442,  4302,  3740,  2815,  2031,  1458,  1054,   678,   827,  36.0
  2020-07-05,  1109,  1189,  1523,  4112,  7213,  7311,  6944,  5950,  5556,  5756,  5536,  4986,  3753,  2698,  1995,  1488,  1060,  1303,  39.0
  2020-07-12,  1369,  1380,  1926,  4465,  7200,  7551,  7433,  6799,  6615,  6596,  6532,  5917,  4582,  3431,  2575,  1906,  1426,  1741,  41.0
  2020-07-19,  1407,  1408,  2016,  4131,  6280,  6396,  6676,  6346,  5967,  6246,  6031,  5492,  4407,  3265,  2444,  1874,  1360,  1775,  41.0
  2020-07-26,  1120,  1247,  1695,  3521,  5206,  5246,  5633,  5433,  4955,  5366,  5257,  5084,  3840,  2893,  2136,  1561,  1238,  1557,  42.0
  2020-08-02,   768,   928,  1229,  2371,  3531,  3884,  4003,  3992,  3791,  3759,  3740,  3578,  2880,  2126,  1586,  1181,   861,  1232,  42.0
  2020-08-09,   715,   857,  1222,  2252,  3250,  3331,  3464,  3448,  3229,  3368,  3381,  3171,  2459,  1823,  1499,  1103,   844,  1243,  42.0
  2020-08-16,   551,   595,   811,  1509,  2083,  2234,  2267,  2224,  2103,  2203,  2191,  2178,  1729,  1334,  1049,   814,   639,   826,  43.0
  2020-08-23,   414,   493,   656,  1355,  1756,  1615,  1590,  1575,  1487,  1623,  1657,  1560,  1303,  1024,   857,   689,   504,   700,  43.0
  2020-08-30,   438,   547,   676,  2535,  2952,  1897,  1867,  1775,  1640,  1772,  1811,  1660,  1435,  1082,   879,   650,   525,   765,  39.0
  2020-09-06,   334,   431,   513,  2320,  2356,  1199,  1188,  1176,  1130,  1145,  1145,  1123,  1021,   798,   664,   514,   396,   516,  37.0
  2020-09-13,   323,   348,   562,  2421,  2733,  1482,  1481,  1280,  1299,  1363,  1317,  1291,  1056,   838,   714,   553,   434,   575,  37.0
  2020-09-20,   291,   389,   558,  1676,  1932,  1334,  1241,  1219,  1092,  1210,  1210,  1258,  1003,   727,   646,   491,   357,   401,  39.0
(Last period's data may be incomplete. Age unknown for 1840 out of 700564 cases.)
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
