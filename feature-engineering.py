import csv
import sqlite3
import numpy as np

cities = "complete-data/eligible-cities.csv"
database = "cleaned-data/cleaned-weather-fire-data.db"

with open(cities, "r", newline="") as cities:
		reader = csv.reader(cities)
		eligibleCities = [row[0] for row in list(reader)[1:]]

connection = sqlite3.connect(database)
cursor = connection.cursor()

inc1, inc2, inc3 = 50, 150, 350
attributeList = ["city","date","avgDBT","avgDPT","avgPress","avgSkyCov","avgWSpd","avgWndDir","totalSatGHI","totalSatDNI","avgPresWth","totalRain","avgVisib","avgCeil","fire_breakout","fire_name","end_date","acres_burned"]
colsInc1 = [f"avgDBT_{inc1}", f"avgDPT_{inc1}", f"avgPress_{inc1}", f"avgSkyCov_{inc1}", f"avgWSpd_{inc1}", f"totalSatGHI_{inc1}", f"totalSatDNI_{inc1}", f"totalRain_{inc1}", f"avgVisib_{inc1}", f"avgCeil_{inc1}"]
colsInc2 = [f"avgDBT_{inc2}", f"avgDPT_{inc2}", f"avgPress_{inc2}", f"avgSkyCov_{inc2}", f"avgWSpd_{inc2}", f"totalSatGHI_{inc2}", f"totalSatDNI_{inc2}", f"totalRain_{inc2}", f"avgVisib_{inc2}", f"avgCeil_{inc2}"]
colsInc3 = [f"avgDBT_{inc3}", f"avgDPT_{inc3}", f"avgPress_{inc3}", f"avgSkyCov_{inc3}", f"avgWSpd_{inc3}", f"totalSatGHI_{inc3}", f"totalSatDNI_{inc3}", f"totalRain_{inc3}", f"avgVisib_{inc3}", f"avgCeil_{inc3}"]

with open(f'aggregate-features.csv', 'w', newline='') as outputFile:
	outputWrite = csv.writer(outputFile)
	outputWrite.writerow(np.concatenate((attributeList[:-4], colsInc1, colsInc2, colsInc3, attributeList[-4:])))

	for city in eligibleCities:
		cursor.execute(f"SELECT * FROM \"cleaned-weather-fire-data\" WHERE city = \"{city}\"")
		queryResult = cursor.fetchall()
		npAttributes = np.array([row[2:len(row)-4] for row in queryResult])

		for count, row in enumerate(queryResult):
			# #need nulls so that fire breakout isnt messed up when writing to csv
			# inc1ValuesCombined, inc2ValuesCombined, inc3ValuesCombined = [None for i in colsInc1], [None for i in colsInc2], [None for i in colsInc3]

			#need these checks for partial rolling averages/totals
			if count >= (inc1-1):
				inc1Len = inc1
			else:
				inc1Len = (count+1)
			inc1Values = np.sum(npAttributes[count-(inc1Len-1):count+1], axis=0)
			avgDBT_inc1 = inc1Values[0]/inc1Len
			avgDPT_inc1 = inc1Values[1]/inc1Len
			avgPress_inc1 = inc1Values[2]/inc1Len
			avgSkyCov_inc1 = inc1Values[3]/inc1Len
			avgWSpd_inc1 = inc1Values[4]/inc1Len
			# avgWndDir_inc1 = inc1Values[5]/inc1Len
			totalSatGHI_inc1 = inc1Values[6]
			totalSatDNI_inc1 = inc1Values[7]
			# avgPresWth_inc1 = inc1Values[8]/inc1Len
			totalRain_inc1 = inc1Values[9]
			avgVisib_inc1 = inc1Values[10]/inc1Len
			avgCeil_inc1 = inc1Values[11]/inc1Len
			inc1ValuesCombined = [avgDBT_inc1, avgDPT_inc1, avgPress_inc1, avgSkyCov_inc1, avgWSpd_inc1, totalSatGHI_inc1, totalSatDNI_inc1, totalRain_inc1, avgVisib_inc1, avgCeil_inc1]
			inc1ValuesCombined = [round(i) for i in inc1ValuesCombined]

			if count >= (inc2-1):
				inc2Len = inc2
			else:
				inc2Len = (count+1)
			inc2Values = np.sum(npAttributes[count-(inc2Len-1):count+1], axis=0)
			avgDBT_inc2 = inc2Values[0]/inc2Len
			avgDPT_inc2 = inc2Values[1]/inc2Len
			avgPress_inc2 = inc2Values[2]/inc2Len
			avgSkyCov_inc2 = inc2Values[3]/inc2Len
			avgWSpd_inc2 = inc2Values[4]/inc2Len
			# avgWndDir_inc2 = inc2Values[5]/inc2Len
			totalSatGHI_inc2 = inc2Values[6]
			totalSatDNI_inc2 = inc2Values[7]
			# avgPresWth_inc2 = inc2Values[8]/inc2Len
			totalRain_inc2 = inc2Values[9]
			avgVisib_inc2 = inc2Values[10]/inc2Len
			avgCeil_inc2 = inc2Values[11]/inc2Len
			inc2ValuesCombined = [avgDBT_inc2, avgDPT_inc2, avgPress_inc2, avgSkyCov_inc2, avgWSpd_inc2, totalSatGHI_inc2, totalSatDNI_inc2, totalRain_inc2, avgVisib_inc2, avgCeil_inc2]
			inc2ValuesCombined = [round(i) for i in inc2ValuesCombined]

			if count >= (inc3-1):
				inc3Len = inc3
			else:
				inc3Len = (count+1)
			inc3Values = np.sum(npAttributes[count-(inc3Len-1):count+1], axis=0)
			avgDBT_inc3 = inc3Values[0]/inc3Len
			avgDPT_inc3 = inc3Values[1]/inc3Len
			avgPress_inc3 = inc3Values[2]/inc3Len
			avgSkyCov_inc3 = inc3Values[3]/inc3Len
			avgWSpd_inc3 = inc3Values[4]/inc3Len
			# avgWndDir_inc3 = inc3Values[5]/inc3Len
			totalSatGHI_inc3 = inc3Values[6]
			totalSatDNI_inc3 = inc3Values[7]
			# avgPresWth_inc3 = inc3Values[8]/inc3Len
			totalRain_inc3 = inc3Values[9]
			avgVisib_inc3 = inc3Values[10]/inc3Len
			avgCeil_inc3 = inc3Values[11]/inc3Len
			inc3ValuesCombined = [avgDBT_inc3, avgDPT_inc3, avgPress_inc3, avgSkyCov_inc3, avgWSpd_inc3, totalSatGHI_inc3, totalSatDNI_inc3, totalRain_inc3, avgVisib_inc3, avgCeil_inc3]
			inc3ValuesCombined = [round(i) for i in inc3ValuesCombined]

			outputWrite.writerow(np.concatenate((row[:-4], inc1ValuesCombined, inc2ValuesCombined, inc3ValuesCombined, row[-4:])))