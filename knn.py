import sqlite3
# from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MinMaxScaler#, normalize
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

#omits city, date, and fire info per row
def getWeatherVals(arrList):
	return np.array([arr[2:-4] for arr in arrList])

#omits unnecessary info, scales, and normalizes each row
def getFormattedWeatherVals(arrList):
	vals = getWeatherVals(arrList)
	vals = scaler.transform(vals)
	# vals = svd.transform(vals)
	# vals = normalize(vals)
	return vals

#gets numerical fire info in the form [[fire_breakout (0 or 1), acres_burned (0 or value)], ...]
def getFireDetails(arrList):
	return np.array([[arr[-4], 0 if arr[-1] == None else arr[-1]] for arr in arrList])

printSimilar = False
def getNeighborVals(title, knnFunc, arr):
	outbreakValue = 0

	dists, indices = knnFunc[0][0], knnFunc[1][0]
	if printSimilar:
		print(f"-----{title.upper()}----")
	for count, i in enumerate(indices):
		similarityScore = 1-dists[count]
		similarRow = arr[i]

		if printSimilar:
			print("similarity:", similarityScore)
			print(arr[i])
			print("//")

		outbreakValue += similarityScore*similarRow[-4]

	# print(outbreakValue)
	return outbreakValue

def topSimilar(originalVec):
	city = originalVec[0]
	originalWeather = getFormattedWeatherVals([originalVec])

	#create knn models for city if not already exists (should only apply for the first step of validation/testing data)
	if city not in cityKnnModels:
		print(f"\n{city}")
		print("knn models NOT FOUND, creating...")

		#model for same city only, fires and non fires included
		cursor.execute(f"SELECT * FROM training WHERE city = \"{city}\"")
		queryResult = cursor.fetchall()
		sameCityData = queryResult
		sameCityWeather = getFormattedWeatherVals(queryResult)
		sameCityFire = getFireDetails(queryResult)
		knnSameCity = KNeighborsClassifier(n_neighbors=sameCityNumNeighbors, metric="cosine", weights="distance")
		knnSameCity.fit(sameCityWeather, sameCityFire)
		print("same city knn done")

		#model for all every other city data, fires and non fires included
		cursor.execute(f"SELECT * FROM training WHERE city != \"{city}\"")
		queryResult = cursor.fetchall()
		otherCityData = queryResult
		otherCityWeather = getFormattedWeatherVals(queryResult)
		otherCityFire = getFireDetails(queryResult)
		knnOtherCity = KNeighborsClassifier(n_neighbors=otherCityNumNeighbors, metric="cosine", weights="distance")
		knnOtherCity.fit(otherCityWeather, otherCityFire)
		print("other city done")

		cityKnnModels[city] = [knnSameCity, knnOtherCity, sameCityData, otherCityData]

	# print(originalVec[1])
	# print(f"~~~~~\n{originalVec}")
	a = getNeighborVals("same city", cityKnnModels[city][0].kneighbors(originalWeather), cityKnnModels[city][2]) / sameCityNumNeighbors * sameCityWeight
	b = getNeighborVals("other city", cityKnnModels[city][1].kneighbors(originalWeather), cityKnnModels[city][3]) / otherCityNumNeighbors * otherCityWeight
	c = getNeighborVals("fire", knnFires.kneighbors(originalWeather), fireData) / fireNumNeighbors * fireWeight
	return a + b + c
	
database = "split-data.db"
connection = sqlite3.connect(database)
cursor = connection.cursor()
# fireNumNeighbors, sameCityNumNeighbors, otherCityNumNeighbors = 20, 150, 7000
# fireWeight, sameCityWeight, otherCityWeight = .35, .45, .2
# 16.875511396843947/28
fireNumNeighbors, sameCityNumNeighbors, otherCityNumNeighbors = 35, 200, 10000
fireWeight, sameCityWeight, otherCityWeight = .45, 0.35, 0.2
cityKnnModels = {}

if not np.isclose([fireWeight+sameCityWeight+otherCityWeight], [1]):
	raise ValueError(fireWeight + sameCityWeight + otherCityWeight)

#fitting scalers based on entire training data
cursor.execute("SELECT * FROM training")
queryResult = cursor.fetchall()
# trainingData = queryResult #save the training data for future reference

queryVals = getWeatherVals(queryResult) #cant modify yet bc need to fit scalers
scaler = MinMaxScaler()
queryVals = scaler.fit_transform(queryVals)
# svd = TruncatedSVD(n_components=30)
# queryVals = svd.fit_transform(queryVals)
print("fitting done")

#model for fires only
cursor.execute("SELECT * FROM training WHERE fire_breakout = 1") #only get fire data
queryResult = cursor.fetchall()
fireData = queryResult
fireWeather = getFormattedWeatherVals(queryResult)
fireDetails = getFireDetails(queryResult)

knnFires = KNeighborsClassifier(n_neighbors=fireNumNeighbors, metric="cosine", weights="distance")
knnFires.fit(fireWeather, fireDetails)
print("knn fire done")

cursor.execute("SELECT * FROM validation")
# cursor.execute("SELECT * FROM validation WHERE date > \"2021-03-13\" AND date < \"2021-03-16\"")
queryResult = cursor.fetchall()
date = ""

daysWithFires = {}
predictions = {}
dailyCityPreds = []
fireOnDate = False
for validationRow in queryResult:
	city = validationRow[0]
	rowDate = validationRow[1]

	if rowDate != date:
		if fireOnDate:
			predictions[date] = sorted(dailyCityPreds, key=lambda x: x[1], reverse=True)
		dailyCityPreds = []
		fireOnDate = False
		date = rowDate
		print(date)

	if validationRow[-4] == 1:
		fireOnDate = True
		if rowDate in daysWithFires:
			daysWithFires[rowDate].append(city)
		else:
			daysWithFires[rowDate] = [city]

	prob = topSimilar(validationRow)
	dailyCityPreds.append((city, prob))

score = 0
numFires = 0
print("\n\n\n")
print(daysWithFires)
print(predictions)
for key in daysWithFires:
	confirmedFires = daysWithFires[key]
	cityRankings = [i[0] for i in predictions[key]]
	for city in confirmedFires:
		numFires += 1
		score += (len(cityRankings) - cityRankings.index(city))/len(cityRankings)

print(f"\n{score}/{numFires}")