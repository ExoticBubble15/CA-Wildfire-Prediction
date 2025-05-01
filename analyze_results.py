decimals = 3
def pointsBased(confirmed, predictions, results):
	results.write("POINTS-BASED SCORING")
	score = 0
	maxPoints = 0
	for date in confirmed:
		str = f'{date}: '
		confirmedFires = confirmed[date]
		maxPoints += len(confirmedFires)

		cityRankingsDupes = ([i[0] for i in predictions[date]])
		cityRankings = []
		for i in cityRankingsDupes:
			if i not in cityRankings:
				cityRankings.append(i)
		for city in confirmedFires:
			predictedPosition = cityRankings.index(city)
			pointsAwarded = round((len(cityRankings) - predictedPosition)/len(cityRankings), decimals)
			score += pointsAwarded

			str += f'{city} | predicted position: {predictedPosition}/{len(cityRankings)}, points awarded: {pointsAwarded} /// '
		results.write(f'\n{str}')

	score = round(score, decimals)
	improvement = round((score - maxPoints/2)/(maxPoints/2)*100, decimals)
	inc = "increase"
	if improvement < 0:
		inc = "decrease"
	results.write(f"\npredicted = {score}/{maxPoints} | random = {maxPoints/2}/{maxPoints} -> {improvement}% {inc} from random")

def percentileBased(sol, guess, results):
	results.write("PERCENTILE-BASED")
	for divisor in [10,5,4,3,2] :
		correctPredictions = 0
		totalFires = 0
		for date in sol:
			confirmed = sol[date]
			totalFires += len(confirmed)

			predicted = [i[0] for i in guess[date]]
			predicted = predicted[0:len(predicted)//divisor]

			for i in confirmed:
				if i in predicted:
					correctPredictions += 1
		
		randomCorrectPredictions = round(totalFires/divisor, decimals)
		improvement = round((correctPredictions - randomCorrectPredictions) / randomCorrectPredictions * 100, decimals)
		a = "increase"
		if improvement < 0:
			a = "decrease"
			improvement *= -1
		results.write(f'\ntop {round(100/divisor,1)}%: predicted = {correctPredictions}/{totalFires} | random = {randomCorrectPredictions}/{totalFires} -> {improvement}% {a} from random')

def evaluateResults(confirmed, predictions, fileName):
	with open(f"{fileName}.txt", "w") as results:
		pointsBased(confirmed, predictions, results)
		results.write("\n\n")
		percentileBased(confirmed, predictions, results)