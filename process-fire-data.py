import sys
import csv
import reverse_geocode

def process(csv_data, export_name="complete-fire-data"):
	data = csv.reader(open(csv_data, "r"))

	with open(f'{export_name}.csv', 'w', newline='') as outputFile:
		outputWrite = csv.writer(outputFile)
		outputWrite.writerow(["fire_name", "city", "start_date", "end_date", "acres_burned"]) #first row = attributes

		firstRow = True
		for row in data:
			try:
				if firstRow:
					firstRow = False
					continue
				longitude = row[12]
				latitude = row[13]
				result = reverse_geocode.get((latitude, longitude))
				# print(result)
				if result["state"] == "California": #add some filtering to only include results that begin in city with data
					fire_name = row[0]
					city = result["city"]
					start_date = row[19]
					end_date = row[18]
					acres_burned = row[8]

					if fire_name != "" and start_date != "" and int(acres_burned) > 0 and end_date != "" and city != "":
						if int(start_date[0:4]) >= 2014 and int(start_date[0:4]) <= 2024:
							outputWrite.writerow([fire_name, city, start_date, end_date, acres_burned])
			except:
				pass

if __name__ == "__main__":
    #python process-fire-data.py <input_csv_file> <optional: export_file_name>
	if len(sys.argv) == 2:
		process(sys.argv[1])
	elif len(sys.argv) == 3:
		process(sys.argv[1], sys.argv[2])
	else:
		print("incorrect number of arguments")
		sys.exit(1)