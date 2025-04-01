import sys
import csv
import sqlite3
import matplotlib.pyplot as plt
import datetime

def daysBetween(day1, day2):
	day1 = datetime.datetime.strptime(day1, "%Y-%m-%d")
	day2 = datetime.datetime.strptime(day2, "%Y-%m-%d")
	return (day2-day1).days

def visualize(argsList):
	cities = "complete-data/eligible-cities.csv"
	database = "cleaned-data/cleaned-weather-fire-data.db"

	#verifying arguments
	if len(argsList) > 4 or len(argsList) < 3:
		raise Exception("insufficient number of arguments")

	city = argsList[0]
	with open(cities, "r", newline="") as cities:
		reader = csv.reader(cities)
		eligibleCities = [row[0] for row in list(reader)[1:]]
	if city not in eligibleCities:
		raise Exception(f'{city} is an invalid city')
	print(city)

	attributeList = ["city","date","avgDBT","avgDPT","avgPress","avgSkyCov","avgWSpd","avgWndDir","totalSatGHI","totalSatDNI","avgPresWth","totalRain","avgVisib","avgCeil","fire_breakout","fire_name","end_date","acres_burned"]
	getAttributeName = [None, None, None]
	for attributeCount, attribute in enumerate(argsList[1:]):
		if attribute == "default":
			getAttributeName[attributeCount] = "days since last fire"
		elif attribute in attributeList:
			getAttributeName[attributeCount] = attribute
		else:
			raise Exception(f'{attribute} is not an attribute')
	print("all attibutes valid")

	#setting up graph
	fig = plt.figure(figsize=(13, 6))
	xLabel, yLabel, zLabel = getAttributeName[0], getAttributeName[1], getAttributeName[2]
	if getAttributeName[2]:
		ax = fig.add_subplot(projection='3d')
		ax.set_xlabel(xLabel)
		ax.set_ylabel(yLabel)
		ax.set_zlabel(zLabel)
		plt.title(f'{city}: {xLabel}, {yLabel}, {zLabel} (2014-2024)')
	else:
		ax = fig.add_subplot()
		ax.set_xlabel(xLabel)
		ax.set_ylabel(yLabel)
		plt.title(f'{city}: {xLabel}, {yLabel} (2014-2024)')

	#getting data from db
	connection = sqlite3.connect(database)
	cursor = connection.cursor()
	cursor.execute(f"SELECT * FROM \"cleaned-weather-fire-data\" WHERE city = \"{city}\"")
	queryResult = cursor.fetchall()

	"""
	- code for making each line toggable is from 
		https://learndataanalysis.org/source-code-how-to-toggle-graphs-visibility-by-clicking-legend-label-in-matplotlib/,
		with modifications made with assisatance from chatgpt (https://chatgpt.com/)
	- chatgpt was used exclusively for this function
	- all such lines are indicated via '##!'
	"""
	#plotting data
	#legend is in the form: <fire number> <city> <fire breakout date> (<days since previous fire>)
	mostRecentFire = "2013-12-31" #right before start of data
	fireCounter = 0
	xAtts, yAtts, zAtts = [], [], []
	lines = []
	for row in queryResult:
		date = row[attributeList.index("date")]
		fireBreakout = True if row[attributeList.index("fire_breakout")] == 1 else False

		for attCounter, att in enumerate(argsList[1:]):
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

		if fireBreakout:
			fireCounter += 1
			if getAttributeName[2]:
				lines.append(ax.plot(xAtts, yAtts, zAtts, label=f'{fireCounter} {city} {date} ({daysBetween(mostRecentFire, date)})', marker='o', markevery=[-1], markersize=7, markeredgecolor='black')[0]) ##!
			else:
				lines.append(ax.plot(xAtts, yAtts, label=f'{fireCounter} {city} {date} ({daysBetween(mostRecentFire, date)})', marker='o', markevery=[-1], markersize=7, markeredgecolor='black')[0]) ##!
			xAtts, yAtts, zAtts = [], [], []
			mostRecentFire = date

	#data from most recent fire to present
	# if getAttributeName[2]:
	# 	lines.append(ax.plot(xAtts, yAtts, zAtts, label=f'end {city} {date} ({daysBetween(mostRecentFire, date)})', marker='o', markevery=[-1], markersize=7, markeredgecolor='black')[0]) ##!
	# else:
	# 	lines.append(ax.plot(xAtts, yAtts, label=f'end {city} {date} ({daysBetween(mostRecentFire, date)})', marker='o', markevery=[-1], markersize=7, markeredgecolor='black')[0]) ##!
	print(f'{fireCounter} fires')

	#begin ##!
	leg = ax.legend(fontsize='small', loc='upper right')
	leg.set_draggable(True)
	lined = dict()
	for legline, origline in zip(leg.get_lines(), lines):
		legline.set_picker(5)
		lined[legline] = origline

	def onpick(event):
		legline = event.artist
		if legline not in lined:
			return
		origline = lined[legline]
		vis = not origline.get_visible()
		origline.set_visible(vis)
		if vis:
			legline.set_alpha(1.0)
		else:
			legline.set_alpha(0.2)
		fig.canvas.draw()

	fig.canvas.mpl_connect('pick_event', onpick)
	#end ##!

	plt.show()

if __name__ == "__main__":
	#python graph-city-attributes.py <city> <x-axis attribute> <y-axis attribute> <optional: z-axis attribute>
	#use 'default' as param for days since last fire
	visualize(sys.argv[1:])