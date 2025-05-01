import sqlite3
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
import numpy as np
import datetime
import matplotlib.pyplot as plt

def daysBetween(day1, day2):
	day1 = datetime.datetime.strptime(day1, "%Y-%m-%d")
	day2 = datetime.datetime.strptime(day2, "%Y-%m-%d")
	return (day2-day1).days

#gets weather features from each row
def getWeatherVals(arrList):
	return np.array([arr[2:-4] for arr in arrList])

#gets normalized weather features for each row
def normalizedWeatherVals(arrList):
	return normalize(getWeatherVals(arrList))

#gets list of fire outbreaks [fire_breakout (0 or 1), ...]
def getFireDetails(arrList):
	# return np.array([[arr[-4], 0 if arr[-1] == None else arr[-1]] for arr in arrList])
	return np.array([arr[-4] for arr in arrList])

const = 350*2
def weightFunction(daysBetween):
	return np.e**(-((daysBetween-1)/const))

printSimilar = False
def getNeighborVals(title, nnFunc, rows, date):
	score = 0
	numFires = 0
	dists, indices = nnFunc[0][0], nnFunc[1][0]

	if printSimilar:
		print(f"-----{title.upper()}----")
	for count, i in enumerate(indices):
		similarityScore = 1-dists[count]
		similarRow = rows[i]

		if printSimilar:
			print("similarity:", similarityScore)
			print(rows[i])
			print("//")
		if similarRow[-4] == 1:
			numFires += 1

		score += similarityScore * similarRow[-4] * weightFunction(daysBetween(similarRow[1], date))

	# print(f"{title} {score/len(dists)} {numFires}") 
	return score/len(dists)

def topSimilar(originalVec):
	city = originalVec[0]
	date = originalVec[1]
	originalWeather = normalizedWeatherVals([originalVec])
	# print(f"\n{originalVec}")

	#create nn models for city if not already exists (should only execute in the first step of validation/testing data)
	if city not in cityNnModels:
		print(f"\n{city}")
		print("nn models NOT FOUND, creating...")

		#model with all rows from city only (training only)
		cursor.execute(f"SELECT * FROM \"engineered-training\" WHERE city = \"{city}\"")
		queryResult = cursor.fetchall()
		sameCityRows = queryResult
		sameCityWeather = normalizedWeatherVals(queryResult)
		nnSameCity = NearestNeighbors(n_neighbors=sameCityNumNeighbors, metric="cosine")
		nnSameCity.fit(sameCityWeather)
		print("same city nn done")

		#model with all rows from all other cities (training only)
		cursor.execute(f"SELECT * FROM \"engineered-training\" WHERE city != \"{city}\"")
		queryResult = cursor.fetchall()
		otherCityRows = queryResult
		otherCityWeather = normalizedWeatherVals(queryResult)
		nnOtherCity = NearestNeighbors(n_neighbors=otherCityNumNeighbors, metric="cosine")
		nnOtherCity.fit(otherCityWeather)
		print("other city done")

		cityNnModels[city] = [nnSameCity, nnOtherCity, sameCityRows, otherCityRows]

	a = getNeighborVals("same city", cityNnModels[city][0].kneighbors(originalWeather), cityNnModels[city][2], date) * sameCityWeight
	b = getNeighborVals("other city", cityNnModels[city][1].kneighbors(originalWeather), cityNnModels[city][3], date) * otherCityWeight
	c = getNeighborVals("fire", nnFires.kneighbors(originalWeather), fireRows, date) * fireWeight

	# print(f"FINAL SCORE: {a+b+c}")
	return a+b+c
	
database = "engineered-subsets.db"
connection = sqlite3.connect(database)
cursor = connection.cursor()

fireNumNeighbors, sameCityNumNeighbors, otherCityNumNeighbors = 20, 100, 7000
fireWeight, sameCityWeight, otherCityWeight = .6, .15, .25
cityNnModels = {}

if not np.isclose([fireWeight+sameCityWeight+otherCityWeight], [1]):
	raise ValueError("weights must add to 1")

#model for fires only
cursor.execute("SELECT * FROM \"engineered-training\" WHERE fire_breakout = 1") #only get fire data
queryResult = cursor.fetchall()
fireRows = queryResult
fireWeather = normalizedWeatherVals(queryResult)

nnFires = NearestNeighbors(n_neighbors=fireNumNeighbors, metric="cosine")
nnFires.fit(fireWeather)
print("nn fire done")

cursor.execute("SELECT * FROM \"engineered-testing\" ORDER BY date, city")
queryResult = cursor.fetchall()
date = ""

# plt.figure(figsize=(13, 6))
# xA = []
# yA = []
# for row in queryResult:
# 	b, x, y = topSimilar(row)
# 	xA.append(x)
# 	yA.append(y)
# 	if b:
# 		plt.plot(xA, yA)
# 		xA, yA = [], []
# plt.plot(xA, yA)
# plt.show()

daysWithFires = {}
predictions = {}
dailyCityPreds = []
fireOnDate = False
for row in queryResult:
	city = row[0]
	rowDate = row[1]

	if rowDate != date:
		if fireOnDate:
			predictions[date] = sorted(dailyCityPreds, key=lambda x: x[1], reverse=True)
		dailyCityPreds = []
		fireOnDate = False
		date = rowDate
		print(date)

	if row[-4] == 1:
		fireOnDate = True
		if rowDate in daysWithFires:
			daysWithFires[rowDate].append(city)
		else:
			daysWithFires[rowDate] = [city]

	score = topSimilar(row)
	dailyCityPreds.append((city, score))