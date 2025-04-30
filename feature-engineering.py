import csv
import sqlite3
import numpy as np
import datetime

def daysBetween(day1, day2):
	day1 = datetime.datetime.strptime(day1, "%Y-%m-%d")
	day2 = datetime.datetime.strptime(day2, "%Y-%m-%d")
	return (day2-day1).days

def square_sign(dayValue, average):
	diff = dayValue - average
	if diff < 0: #daily value is below average
		return -(diff**2)
	return diff**2 #daily value is above average

cities = "complete-data/eligible-cities.csv"
database = "cleaned-data/cleaned-subsets.db"

with open(cities, "r", newline="") as cities:
		reader = csv.reader(cities)
		eligibleCities = [row[0] for row in list(reader)[1:]]

connection = sqlite3.connect(database)
cursor = connection.cursor()
#keeping track to use in engineered validation/testing 
cityTrainingMeans = {}
lastFireDates = {}
rollingTotals = {} #key: city, value: [totalSatGHI, totalSatDNI, totalRain]
dayBeforeDataStart = "2013-12-31" #right before start of data

attributeList = ["city","date","avgDBT","avgDPT","avgPress","avgSkyCov","avgWSpd","avgWndDir","totalSatGHI","totalSatDNI","avgPresWth","totalRain","avgVisib","avgCeil","fire_breakout","fire_name","end_date","acres_burned"]
newAtts = ["avgDBT_deviation","avgDPT_deviation","avgPress_deviation","avgSkyCov_deviation","avgWSpd_deviation","avgWndDir_deviation","totalSatGHI_since_last_fire","totalSatDNI_since_last_fire","avgPresWth_deviation","totalRain_since_last_fire","avgVisib_deviation","avgCeil_deviation", "days_since_last_fire"]

subsets = ["training", "validation", "testing"]
for i in range(3):
	with open(f'engineered-{subsets[i]}.csv', 'w', newline='') as outputFile:
		outputWrite = csv.writer(outputFile)
		outputWrite.writerow(np.concatenate((attributeList[:-4], newAtts, attributeList[-4:])))
	
		for city in eligibleCities:
			cursor.execute(f"SELECT * FROM \"cleaned-{subsets[i]}\" WHERE city = \"{city}\"")
			queryResult = cursor.fetchall()
			
			if i == 0: #initialize cityTrainingMeans and rollingTotals on training
				print("means and rolling totals initialized")
				cityTraining = np.array([row[2:-4] for row in queryResult]) #only weather data
				cityTrainingMeans[city] = np.round(np.mean(cityTraining, axis=0)).astype(int)
				rollingTotals[city] = [0,0,0] #key: city, value: [totalSatGHI, totalSatDNI, totalRain]
				lastFireDates[city] = dayBeforeDataStart
			
			means = cityTrainingMeans[city]

			for row in queryResult:
				date = row[1]
				rollingTotals[city][0] += row[8]
				rollingTotals[city][1] += row[9]
				rollingTotals[city][2] += row[11]
				vals = row[2:-4]

				avgDBT_deviation = square_sign(vals[0], means[0])
				avgDPT_deviation = square_sign(vals[1], means[1])
				avgPress_deviation = square_sign(vals[2], means[2])
				avgSkyCov_deviation = square_sign(vals[3], means[3])
				avgWSpd_deviation = square_sign(vals[4], means[4])
				avgWndDir_deviation = square_sign(vals[5], means[5])
				totalSatGHI_since_last_fire = rollingTotals[city][0]
				totalSatDNI_since_last_fire = rollingTotals[city][1]
				avgPresWth_deviation = square_sign(vals[8], means[8])
				totalRain_since_last_fire = rollingTotals[city][2]
				avgVisib_deviation = square_sign(vals[10], means[10])
				avgCeil_deviation = square_sign(vals[11], means[11])
				days_since_last_fire = daysBetween(lastFireDates[city], date)

				if row[-4] == 1: #fire breakout
					rollingTotals[city] = [0,0,0] #key: city, value: [totalSatGHI, totalSatDNI, totalRain]
					lastFireDates[city] = date

				newFeatures = [avgDBT_deviation,avgDPT_deviation,avgPress_deviation,avgSkyCov_deviation,avgWSpd_deviation,avgWndDir_deviation,totalSatGHI_since_last_fire,totalSatDNI_since_last_fire,avgPresWth_deviation,totalRain_since_last_fire,avgVisib_deviation,avgCeil_deviation,days_since_last_fire]

				outputWrite.writerow(np.concatenate((row[:-4], newFeatures, row[-4:])))

			if i == 0:
				print(f"{city} TRAINING MEANS")
				print([(attributeList[2:-4][i], means[i]) for i in range(len(means))], "\n")
			else:
				print(f"{city} {subsets[i].upper()}")
	print()