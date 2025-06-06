# data-filtering
Package of functions for simple data filtering. Applications include stream gages.


- Data Filters were referenced from the following Integrated Ocean Observing System (IOOS) manual: 
    - Manual for Real-Time Quality Control of Stream Flow Observations: A Guide to Quality Control andQuality Assurance for Stream Flow Observations in Rivers and Streams, Version 1.0, September 2018, DOI: 10.25923/gszc-ha43
- Threshold Filter
    - The threshold filter takes out any values above or below defined minimum and maximum thresholds.
- Despiking 2-Neighbors
    - The despiking 2-neighbor filter removes spikes based on a tested point’s preceding and following data point. For each test point, the previous and following data point values are averaged. Then, if the test point’s value is outside of a maximum allowable difference, the point is removed.
- Despiking 12-Neighbors
    - The despikeing 12-neighbor filter removes spikes based on a tested point’s preceding and following datapoints, six points before and six points after. This is essentially a moving average filter. The average of the 12 neighboring points is calculated, then the test point is compared based on a maximum allowable difference.
- Rate-of-Rise Filter
    - The rate-of-rise filter is similar to a despiking filter. The gradient is calculated for each point to find the change in value over time. The test point is removed if its rate-of-rise is above the defined threshold, no matter the time difference between measurements.
- Remove Consecutive Duplicates
    - The flat line filter checks for evidence of no data being taken, sometimes indicated by multiple, repeated, consecutive points of the same value.
- NOTE: it is important to implement the filter in this same order. For example, filtering on rate-of-rise does not make sense if spikes are present in the data.
