# California Wildfire Prediction
*Analyzing previous weather data to predict future fires*

## Project Description / Goal
California has a defined history of being extremely susceptible to wildfires, with the recent Palisades and Eaton fires being prime demonstrations of their devastating effects on wildlife and urban communities. This project will aim to develop a model that can identify which area(s) of the state are at the highest risk for a fire to break out, using historical weather and fire data to find a correlation between these factors. 

## Required Data
The model will rely on local weather and fire data across many years to identify relationships between the two and make predictions. In order to be as specific as possible regarding the identification of fire-prone areas, historical climate data per city is required. A comprehensive list of fires, including details on their location and severity, is also needed to identify breakout points and patterns.
- Per city weather data, spanning from 1998 to present, for over 100 cities can be found via the [CALMAC California Weather Files](https://www.calmac.org/weather.asp).
- An extensive list of fires and their details can be found through the [CAL FIRE Incident Data](https://www.fire.ca.gov/incidents), with previous yearly reports from the agency available via their [Past Wildfire Activity Statistics](https://www.fire.ca.gov/our-impact/statistics).

## Modeling
Since the course has not covered data modeling methods beyond clustering, the best approach to modeling the data has not yet been determined. However, a principal idea could be to take a deep learning approach to the problem. This could be done to identify a combination of weather factors that contribute toward or are indicative of a fire outbreak (e.g. identifying how many days since *x* amount of rainfall makes an area more likely to experience a fire starting). Of course, alternative approaches are always being considered once they are introduced and discussed in lecture.

## Visualization
Similarly to the modeling section, I do not have sufficient knowledge of different visualization techniques and thus cannot determine which approach is best for this project's goal. However, by working with the method of identifying at-risk areas based on weather patterns, t-SNE or scatter plots could be used to gain a visual depiction of identified factors and their correlation with fire outbreaks.

## Testing
After all required data has been collected and processed, the majority of the data will be used for training while the remaining portion will be used to test the model. An initial estimate of this split is approximately 70/30, but specific percentages and date ranges will be determined later.
