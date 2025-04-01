# California Wildfire Prediction
*Analyzing previous weather data to predict future fires*

### Midterm Report Presentation
A 5 minute explanation of the current progress can be found [here].

## Project Description / Goal
California has a defined history of being extremely susceptible to wildfires, with the recent Palisades and Eaton fires being prime demonstrations of their devastating effects on wildlife and urban communities. This project will aim to develop a model that can identify which area(s) of the state are at the highest risk for a fire to break out, using historical weather and fire data to find a correlation between these factors. Additionally, the model will determine how much each weather feature contributes towards the area's fire risk.

## Required Data
The model will rely on local weather and fire data across many years to identify relationships between the two and make predictions. In order to be as specific as possible regarding the identification of fire-prone areas, historical climate data per city is required. A comprehensive list of fires, including details on their location and severity, is also needed to identify breakout points and patterns.
- Per city weather data, spanning from 1998 to present, for over 100 cities can be found via the [CALMAC California Weather Files](https://www.calmac.org/weather.asp).
- An extensive list of fires and their details can be found through the [CAL FIRE Incident Data](https://www.fire.ca.gov/incidents), with previous yearly reports from the agency available via their [Past Wildfire Activity Statistics](https://www.fire.ca.gov/our-impact/statistics).

The original weather and fire files that were used to generate the complete dataset can be found [here](https://drive.google.com/drive/folders/1D4q_7aPc9mx8MtHmdEg1-FQKdTX9w-JH).

### Dataset Attributes
Each element in the dataset contains the following attributes:

1. *city* - Name of the city which the following weather data applies for
1. *date* – Date of the recorded weather data
1. *avgDBT* – Average Dry-bulb Temperature (C)
1. *avgDPT* – Average Dew-point Temperature (C) 
1. *avgPress* – Average Pressure (mb)
1. *avgSkyCov* – Average Sky Coverage (tenths)  
1. *avgWSpd* – Average Wind Speed (m/s)
1. *avgWndDir* – Average Wind Direction (degrees)
1. *totalSatGHI* – Total Global Horizontal Irradiance (W/m²)
1. *totalSatDNI* – Total Direct Normal Irradiance (W/m²)
1. *avgPresWth* – Average Present Weather
1. *totalRain* – Total Rainfall (0.1mm) 
1. *avgVisib* – Average Visibility (m)
1. *avgCeil* – Ceiling Height (m) 
1. *fire_breakout* – 1 if a fire broke out on that day, 0 otherwise
1. *fire_name* – Name of the fire  
1. *end_date* – Date when the fire was extinguished
1. *acres_burned* – Total area burnt by the fire (acres) 

Attributes 3 through 14 are as specified in pages 3 and 4 of the [CALMAC Weather Files User Guide](https://www.calmac.org/Weather%20User%20Guide.pdf).

## Visualization
Since each weather data point has more than 3 dimensions, visualizing the data set requires reducing it to 2 or 3 dimensions. This was done by writing a script to track up to 3 attributes of a city's weather data across the entire dataset. This allows for general patterns in fire outbreak to be identified, such as a relatively high DBT (Dry-bulb Temperature) 
or relatively high satellite GHI (global horizontal irradiance). Once a graph is generated, each line represents the tracked attribute(s) between fires, with a fire outbreak indicated by an outlined dot.

Plotting up to 3 selected attributes for all fire breakouts is also available, and further helps identify combinations of weather factors that indicate a fire outbreak. However, doing so omits historical context in the form of data in between outbreaks, as including such data would lead to an overwhelming amount of points and make the graph illegible.

Sample graphs, both in 2d and 3d, can be found in the graphs folder. Most samples contain an axis that tracks how many days have passed since the previous fire outbreak to help with organization. However, this is not necessary as you can track any 3 weather attributes for any city. 

## Modeling
Given the scale of long-term weather data, reducing the size of the data while preserving its variance through techniques like SVD seems like a good approach to modeling. KNN also seems like a viable approach, potentially using cosine similarity as its distance function, as it would allow for identifying and comparing weather features that preceded a fire.

## Validation and Testing
After all the data was collected and processed, the cumulative dataset was divided into training, validation, and testing data based on calendar year and total amount of fires per year. 

This resulted in assigning years 2014-2020 as training data, 2021-2022 as validation data, and 2023-2024 as testing data. These splits contain approximately 71% (170/238), 12% (28/238), and 17% (40/238) of total fire outbreaks respectively.

The specific number of fires per year can be found on lines 171-192 of "sql-queries.txt"