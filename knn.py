import sqlite3
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
import numpy as np
import datetime
import matplotlib.pyplot as plt
import analyze_results
import sys

#gotta nest these big ass functions to make it callable by terminal smh
def search(dataSubset, fileName, start=None, end=None):
	def daysBetween(day1, day2):
		day1 = datetime.datetime.strptime(day1, "%Y-%m-%d")
		day2 = datetime.datetime.strptime(day2, "%Y-%m-%d")
		return (day2-day1).days
	
	dataSubset = dataSubset.lower()
	if dataSubset != "validation" and dataSubset != "testing":
		raise ValueError("dataSubset must be validation or testing ONLY")
	if "." in fileName:
		raise ValueError("dont put '.' in fileName")
	if start == None and end == None: 
		pass
	elif (start == None and end != None) or (start != None and end == None) or start < "2021-01-01" or end > "2024-12-31" or daysBetween(start, end) < 0:
		raise ValueError("incorrect start and end times, start must be >= '2021-01-01', end must be <= '2024-12-31', start must be before end")

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
	# const = 350*6
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

	query = ""
	if start == None:
		query = (f"SELECT * FROM \"engineered-{dataSubset}\" ORDER BY date, city")
	else:
		query = (f"SELECT * FROM \"engineered-{dataSubset}\" WHERE date >= \"{start}\" AND date <= \"{end}\" ORDER BY date, city")
	cursor.execute(query)
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

	print()
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
	
	#in case the last date was a fire
	if fireOnDate:
		predictions[date] = sorted(dailyCityPreds, key=lambda x: x[1], reverse=True)

	# print(daysWithFires)
	# print(predictions)
	analyze_results.evaluateResults(daysWithFires, predictions, fileName, query)

if __name__ == "__main__":
	#python knn.py <validation or testing> <results_file_name> <optional: start_date> <optional: end_date>
	#must have start and end dates together, omitting either will produce output the entire results for validation/testing
	#do not include a file extension for the results_file_name
	#note that the program will error if you run a subset of the validation or testing data, and no fires are present
	if len(sys.argv) == 3 or len(sys.argv) == 5:
		# for i in sys.argv[1:]:
		# 	print(f'{type(i)} |{i}|')
		# print()
		
		if len(sys.argv) == 3:
			search(sys.argv[1], sys.argv[2])
		else: #len(sys.argv) == 5
			search(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	else:
		print("incorrect arguments")
		sys.exit(1)