from zipfile import ZipFile 
import sys
import os
import reverse_geocode
import re
import csv
import time

def doubleDigitNum(num):
	num = str(num)
	if len(num) == 1:
		return f'0{num}'
	return num

def convert(string):
	noLetters = re.sub(r'[^\d.-]', '', string)
	if bool(re.search(r'\d', string)): #contains a number
		try:
			return int(noLetters)
		except ValueError:
			return float(noLetters)
	return string

def process(allYears, export_name="complete-weather-data"):
	startingTime = time.time()
	print("code start")

	with open(f'{export_name}.csv', 'w', newline='') as outputFile:
			outputWrite = csv.writer(outputFile)
			outputWrite.writerow(["city", "date", "avgDBT", "avgDPT", "avgPress", "avgSkyCov", "avgWSpd", "avgWndDir", "totalSatGHI", "totalSatDNI", "avgPresWth", "totalRain", "avgVisib", "avgCeil"])

			yearlyCount = 0
			for yearFolder in os.listdir(allYears):
				yearStart = time.time()
				yearlyCount += 1
				print("---------")
				print(f'{yearlyCount}/{len(os.listdir(allYears))}')
				print(f'START {yearFolder}')

				#unzippping all files
				for zipped in os.listdir(f'{allYears}/{yearFolder}'):
					try:
						with ZipFile(f'{allYears}/{yearFolder}/{zipped}', 'r') as zip:
							zip.extractall(f'{allYears}/{yearFolder}')
						os.remove(f'{allYears}/{yearFolder}/{zipped}')
					except:
						pass
				print("all files unzipped")

				#removing non FIN4 files
				for file in os.listdir(f'{allYears}/{yearFolder}'):
					if not file.endswith(".FIN4"):
						os.remove(f'{allYears}/{yearFolder}/{file}')
				print("all non FIN4 files removed")

				#reading each FIN4 file
				for file in os.listdir(f'{allYears}/{yearFolder}'):
					try:
						# print("FILE ", file)
						with open(f'{allYears}/{yearFolder}/{file}', 'r', encoding='utf-8') as file:
								content = file.read()
								content = content.split("\n")
								content = [[convert(col) for col in row.split()] for row in content]
						
						latitude, longitude = content[0][2], content[0][3]
						result = reverse_geocode.get((latitude, longitude))
						city = result["city"]
						if "california" not in result["state"].lower() or "united states" not in result["country"].lower():
							# print("ERROR")
							# print(file)
							# print(latitude, longitude)
							# print(result)
							# print("------")
							continue
						# print(f'lat: {latitude}, long: {longitude}, city: {reverse_geocode.get((latitude, longitude))["city"]}')

						#getting per day averages
						startIndex = 3
						year, month, day = content[startIndex][0], content[startIndex][1], content[startIndex][2]
						for rowNum in range(startIndex, len(content)): #skip the first 3 rows
							try:
								row = content[rowNum]
								if row == [] or row[1] != month or row[2] != day: #day/month changes = new row; accounts for any missed hourly data
									# date = f'{year}-{month}-{day}'
									date = f'{year}-{doubleDigitNum(month)}-{doubleDigitNum(day)}' #need to match fire data format
									avgDBT, avgDPT, avgPress, avgSkyCov, avgWSpd, avgWndDir, totalSatGHI, totalSatDNI, avgPresWth, totalRain, avgVisib, avgCeil = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

									#12 fields per day
									numEntries = 0
									for i in content[startIndex:rowNum]:
										avgDBT += i[4]
										avgDPT += i[5]
										avgPress += i[6]
										avgSkyCov += i[7]
										avgWSpd += i[9]
										avgWndDir += i[10]
										totalSatGHI += i[11]
										totalSatDNI += i[12]
										avgPresWth += i[13]
										totalRain += i[14]
										avgVisib += i[15]
										avgCeil += i[16]
										numEntries += 1

									#9 averages, 3 totals (rain, satGHI, satDNI)
									avgDBT, avgDPT, avgPress, avgSkyCov, avgWSpd, avgWndDir, avgPresWth, avgVisib, avgCeil = avgDBT/numEntries, avgDPT/numEntries, avgPress/numEntries, avgSkyCov/numEntries, avgWSpd/numEntries, avgWndDir/numEntries, avgPresWth/numEntries, avgVisib/numEntries, avgCeil/numEntries
									# print(date)
									# print(month, day, numEntries)
									# print(f'avgDBT: {avgDBT}, avgDPT: {avgDPT}, avgPress: {avgPress}, avgSkyCov: {avgSkyCov}, avgWSpd: {avgWSpd}, avgWndDir: {avgWndDir}, totalSatGHI: {totalSatGHI}, totalSatDNI: {totalSatDNI}, avgPresWth: {avgPresWth}, totalRain: {totalRain}, avgVisib: {avgVisib}, avgCeil: {avgCeil}')
									# print("----------")
									outputWrite.writerow([city, date, avgDBT, avgDPT, avgPress, avgSkyCov, avgWSpd, avgWndDir, totalSatGHI, totalSatDNI, avgPresWth, totalRain, avgVisib, avgCeil])
									startIndex = rowNum
									if row != []:
										month, day = row[1], row[2]
							except:
								continue
						# print(f'city: {city}, lat: {latitude}, long: {longitude} \n')"
					except:
						continue
				print(f'END {yearFolder}\n{time.time()-yearStart}')
	print(f'---------\ncode end\ntotal time elapsed: {time.time()-startingTime}')

if __name__ == "__main__":
	#python process-weather-data.py <unzipped folder with zipped, per city weather data> <optional: export_file_name>
	if len(sys.argv) == 2:
		process(sys.argv[1])
	elif len(sys.argv) == 3:
		process(sys.argv[1], sys.argv[2])
	else:
		print("incorrect number of arguments")
		sys.exit(1)