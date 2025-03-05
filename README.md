# California Wildfire Prediction
*Analyzing previous weather data to predict future fires*

## Project Description / Goal
California has a defined history of being extremely susceptible to wildfires, with the recent Palisades and Eaton fires being prime demonstrations of their devastating effects on wildlife and urban communities. This project will aim to develop a model that can identify which area(s) of the state are at the highest risk for a fire to break out, using historical weather and fire data to find a correlation between these factors. Additionally, the model will determine how much each weather feature contributes towards the area's fire risk.

## Required Data
The model will rely on local weather and fire data across many years to identify relationships between the two and make predictions. In order to be as specific as possible regarding the identification of fire-prone areas, historical climate data per city is required. A comprehensive list of fires, including details on their location and severity, is also needed to identify breakout points and patterns.
- Per city weather data, spanning from 1998 to present, for over 100 cities can be found via the [CALMAC California Weather Files](https://www.calmac.org/weather.asp).
- An extensive list of fires and their details can be found through the [CAL FIRE Incident Data](https://www.fire.ca.gov/incidents), with previous yearly reports from the agency available via their [Past Wildfire Activity Statistics](https://www.fire.ca.gov/our-impact/statistics).

## Modeling
Given the scale of long-term weather data, reducing the size of the data while preserving its variance through techniques like SVD seems like a good approach to modeling. KNN also seems like a viable approach, potentially using cosine similarity as its distance function, as it would allow for identifying and comparing weather features that preceded a fire.

The initial idea of determining combination of weather factors that indicate fire outbreak via deep learning is still an option, but requires additional research.  

Of course, alternative/additional approaches are always being considered as they are introduced and discussed in lecture.

## Visualization
Since each weather data point has more than 3 dimensions, visualizing the entire data set would require reducing it to 2 dimensions while hopefully preserving patterns and other relationships. This can be done via t-SNE plots or similar methods that depict identified factors and their correlation with fire outbreaks.

As with the modeling section, additional visualization techniques are always considered as the course covers them.

## Testing
After all required data has been collected and processed, the majority of the data will be used for training while the remaining portion will be used to test the model. An initial estimate of this split is approximately 70/30, but specific percentages and date ranges will be determined later.