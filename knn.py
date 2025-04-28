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
def printClosest(title, knnFunc, arr):
	outbreakPercentage = 0

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

		outbreakPercentage += similarityScore*similarRow[-4]

	# print(outbreakPercentage)
	return outbreakPercentage

def topSimilar(originalVec):
	city = originalVec[0]
	originalWeather = getFormattedWeatherVals([originalVec])
	print(f"\n{city}")

	#create knn models for city if not already exists (should only apply for the first step of validation/testing data)
	if city not in cityKnnModels:
		print("knn models NOT FOUND, creating...")

		#model for same city only, fires and non fires included
		cursor.execute(f"SELECT * FROM training WHERE city = \"{city}\"")
		queryResult = cursor.fetchall()
		sameCityData = queryResult
		sameCityWeather = getFormattedWeatherVals(queryResult)
		sameCityFire = getFireDetails(queryResult)
		knnSameCity = KNeighborsClassifier(n_neighbors=sameCityNumNeighbors, metric="cosine")
		knnSameCity.fit(sameCityWeather, sameCityFire)
		print("same city knn done")

		#model for all every other city data, fires and non fires included
		cursor.execute(f"SELECT * FROM training WHERE city != \"{city}\"")
		queryResult = cursor.fetchall()
		otherCityData = queryResult
		otherCityWeather = getFormattedWeatherVals(queryResult)
		otherCityFire = getFireDetails(queryResult)
		knnOtherCity = KNeighborsClassifier(n_neighbors=otherCityNumNeighbors, metric="cosine")
		knnOtherCity.fit(otherCityWeather, otherCityFire)
		print("other city done")

		cityKnnModels[city] = [knnSameCity, knnOtherCity, sameCityData, otherCityData]
	else:
		print("knn models FOUND")

	print(originalVec[1])
	# print(f"~~~~~\n{originalVec}")
	a = printClosest("same city", cityKnnModels[city][0].kneighbors(originalWeather), cityKnnModels[city][2]) / sameCityNumNeighbors * sameCityWeight
	b = printClosest("other city", cityKnnModels[city][1].kneighbors(originalWeather), cityKnnModels[city][3]) / otherCityNumNeighbors * otherCityWeight
	c = printClosest("fire", knnFires.kneighbors(originalWeather), fireData) / fireNumNeighbors * fireWeight
	return a + b + c
	
database = "split-data.db"
connection = sqlite3.connect(database)
cursor = connection.cursor()
fireNumNeighbors, sameCityNumNeighbors, otherCityNumNeighbors = 5, 20, 100
fireWeight, sameCityWeight, otherCityWeight = 0.5/5, 1.5/5, 3/5
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
# svd = TruncatedSVD(n_components=24)
# queryVals = svd.fit_transform(queryVals)
print("fitting done")

#model for fires only
cursor.execute("SELECT * FROM training WHERE fire_breakout = 1") #only get fire data
queryResult = cursor.fetchall()
fireData = queryResult
fireWeather = getFormattedWeatherVals(queryResult)
fireDetails = getFireDetails(queryResult)

knnFires = KNeighborsClassifier(n_neighbors=fireNumNeighbors, metric="cosine")
knnFires.fit(fireWeather, fireDetails)
print("knn fire done")

# cursor.execute("SELECT * FROM validation")
cursor.execute("SELECT * FROM validation WHERE date >= \"2021-03-14\"")
queryResult = cursor.fetchall()

for validationRow in queryResult:
	a = topSimilar(validationRow)
	print(a)