import sqlite3
from sklearn.metrics.pairwise import cosine_similarity as cos_sim
from sklearn.preprocessing import normalize
import numpy as np
import random

# X = [[0, 0, 0], [1, 1, 1]]
# Y = [[1, 0, 0], [1, 1, 0]]
# print(cos_sim(X,Y))

def topSimilar(originalVec, numVecs, sameCity):
	if type(numVecs) != int:
		raise TypeError("numVecs must be an int")
	if type(sameCity) != bool:
		raise TypeError("sameCity must be a bool")

	city = originalVec[0]
	originalVals = np.array([originalVec[2:-4]])

	if sameCity:
		cursor.execute(f"SELECT * FROM training WHERE city = \"{city}\"")
	else:
		cursor.execute(f"SELECT * FROM training WHERE city != \"{city}\"")
	queryResult = cursor.fetchall()
	queryVals = np.array([arr[2:-4] for arr in queryResult])

	originalVals = normalize(originalVals)
	# for arr in queryVals:
	# 	for elem in arr:
	# 		if type(elem) != int:
	# 			raise Exception(arr)
	queryVals = normalize(queryVals)


	print(originalVec)
	# print(originalVals)
	print(len(queryResult), len(queryVals))
	r = random.randint(0, len(queryResult)-1)
	print(queryResult[r])
	print(queryVals[r])
	print(np.linalg.norm(queryVals[r]))


database = "split-data.db"
connection = sqlite3.connect(database)
cursor = connection.cursor()

cursor.execute("SELECT * FROM validation ORDER BY RANDOM() LIMIT 1")
queryResult = cursor.fetchall()[0]
# topSimilar(queryResult,1,True)
topSimilar(queryResult,1,False)

