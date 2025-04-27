import sys
import csv
import sqlite3
import matplotlib.pyplot as plt
import datetime
import random

def random_hex():
	hex_color = '#' + ''.join([random.choice('0123456789abcdef') for j in range(6)])
	return hex_color

def daysBetween(day1, day2):
	day1 = datetime.datetime.strptime(day1, "%Y-%m-%d")
	day2 = datetime.datetime.strptime(day2, "%Y-%m-%d")
	return (day2-day1).days

def visualize(argsList):
	cities = "complete-data/eligible-cities.csv"
	database = "cleaned-data/cleaned-weather-fire-data.db"

	# verifying arguments
	if len(argsList) > 3 or len(argsList) < 2:
		raise Exception("insufficient number of arguments")

	with open(cities, "r", newline="") as cities:
		reader = csv.reader(cities)
		eligibleCities = [row[0] for row in list(reader)[1:]]

	attributeList = ["city","date","avgDBT","avgDPT","avgPress","avgSkyCov","avgWSpd","avgWndDir","totalSatGHI","totalSatDNI","avgPresWth","totalRain","avgVisib","avgCeil","fire_breakout","fire_name","end_date","acres_burned"]
	getAttributeName = [None, None, None]
	for attributeCount, attribute in enumerate(argsList):
		if attribute == "default":
			getAttributeName[attributeCount] = "days since city last fire"
		elif attribute in attributeList:
			getAttributeName[attributeCount] = attribute
		else:
			raise Exception(f'{attribute} is not an attribute')
	print("all attributes valid")

	# setting up graph
	fig = plt.figure(figsize=(13, 6))
	xLabel, yLabel, zLabel = getAttributeName[0], getAttributeName[1], getAttributeName[2]
	if len(argsList) == 3:
		ax = fig.add_subplot(projection='3d')
		ax.set_xlabel(xLabel)
		ax.set_ylabel(yLabel)
		ax.set_zlabel(zLabel)
		plt.title(f'all cities: {xLabel}, {yLabel}, {zLabel} (2014-2024)')
	else:
		ax = fig.add_subplot()
		ax.set_xlabel(xLabel)
		ax.set_ylabel(yLabel)
		plt.title(f'all cities: {xLabel}, {yLabel} (2014-2024)')

	connection = sqlite3.connect(database)
	cursor = connection.cursor()
	totalFires = 0
	for city in eligibleCities:
		cursor.execute(f"SELECT * FROM \"cleaned-weather-fire-data\" WHERE city = \"{city}\"")
		queryResult = cursor.fetchall()

		mostRecentFire = "2013-12-31" #right before start of data
		xAtts, yAtts, zAtts = [], [], []
		clr = random_hex()
		for row in queryResult:
			date = row[attributeList.index("date")]
			fireBreakout = True if row[attributeList.index("fire_breakout")] == 1 else False

			if fireBreakout:
				for attCounter, att in enumerate(argsList):
					value = None
					if att == "default":
						value = daysBetween(mostRecentFire, date)
					else:
						value = row[attributeList.index(att)]

					if attCounter == 0:
						xAtts.append(value)
					elif attCounter == 1:
						yAtts.append(value)
					else:
						zAtts.append(value)
				mostRecentFire = date

		if len(argsList) == 3:
			ax.scatter(xAtts, yAtts, zAtts, label=city, color=clr, s=30)
		else:
			ax.scatter(xAtts, yAtts, label=city, color=clr, s=30)
		totalFires += len(xAtts)

	print(f'{totalFires} fires')
	increment = 250
	ax.set_xticks(range(0, int(ax.get_xlim()[1]+1), increment))
	ax.set_yticks(range(0, int(ax.get_ylim()[1]+1), increment))
	try:
		ax.set_zticks(range(0, int(ax.get_zlim()[1]+1), increment))
	except:
		pass
	leg = ax.legend(fontsize='small', loc='upper right')
	leg.set_draggable(True)
	plt.show()

if __name__ == "__main__":
	#python graph-all-cities-attributes.py <x-axis attribute> <y-axis attribute> <optional: z-axis attribute>
	#use 'default' as param for days since city last fire
	visualize(sys.argv[1:])