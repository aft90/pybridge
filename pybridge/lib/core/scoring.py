from enumeration import Denomination, Seat


# There are undoubtedly many minor variations of the score values.
# In the future, score values may be stored in separate XML format files.


def scoreDuplicate(self, result):
	"""Scoring algorithm for duplicate bridge."""
	score = 0

	isDoubled      = result['contract']['doubleLevel'] == 1
	isRedoubled    = result['contract']['doubleLevel'] == 2
	isVulnerable   = result['vulnerable']
	tricksMade     = result['tricksMade']
	tricksRequired = result['contract']['bidLevel'] + 6
	trumpSuit      = result['contract']['bidDenom']

	if tricksMade >= tricksRequired:
		# Contract fulfilled.

		# Calculate scores for tricks bid and made.
		if trumpSuit in (Denomination.Club, Denomination.Diamond):
			# Clubs and Diamonds score 20 for each odd trick.
			score += contractLevel * 20
		else:
			# Hearts, Spades and NT score 30 for each odd trick.
			score += contractLevel * 30
			if trumpSuit is Denomination.NoTrump:
				score += 10  # For NT, add a 10 point bonus.

		# Calculate scores for doubles.
		if isDoubled:
			score *= 2  # Multiply score by 2 for each isDoubled odd trick.
		elif isRedoubled:
			score *= 4  # Multiply score by 4 for each isRedoubled odd trick.

		# Calculate premium scores.
		if score >= 100:
			if vulnerable:
				score += 500  # Game, vulnerable.
			else:
				# Game, not vulnerable.
				score += 300  # Game, not vulnerable.
			if tricksRequired == 13:
				if vulnerable:
					score += 1500  # Grand slam, vulnerable.
				else:
					score += 1000  # Grand slam, not vulnerable.
			elif contractLevel == 12:
				if vulnerable:
					score += 750  # Small slam, vulnerable.
				else:
					score += 500  # Small slam, not vulnerable.
			
		else:
			score += 50  # Any part score.

		# Calculate "for the insult" bonuses.
		if isDoubled:
			score += 50
		elif isRedoubled:
			score += 100
		
		# Calculate scores for overtricks.
		overTricks = tricksMade - tricksRequired
		if isDoubled:
			if vulnerable:
				# Score 200 for each doubled and vulnerable overtrick.
				score += overTricks * 200
			else:
				# Score 100 for each doubled and not vulnerable overtrick.
				score += overTricks * 100
		elif isRedoubled:
			if vulnerable:
				# Score 400 for each redoubled and vulnerable overtrick.
				score += overTricks * 400
			else:
				score += overTricks * 200
		else:
			if trumpSuit in (Denomination.Club, Denomination.Diamond):
				# Clubs and Diamonds score 20 for each undoubled overtrick.
				score += overTricks * 20
			else:
				# Hearts, Spades and NT score 30 for each undoubled overtrick.
				score += overTricks * 30
	
	else:
		# Contract not fulfilled.

		underTricks = tricksRequired - tricksMade
		if isDoubled:
			if vulnerable:
				# Score 200 for the first doubled and vulnerable undertrick.
				# Score 300 for all other undertricks.
				score -= 200 + (underTricks - 1) * 300
			else:
				# Score 100 for the first doubled and non-vulnerable undertrick.
				# Score 200 for all other undertricks.
				# Score 100 extra for third and greater undertricks.
				score -= 100 + (underTricks - 1) * 200
				if underTricks > 3:
					score -= (underTricks - 3) * 100
		elif isRedoubled:
			if vulnerable:
				score -= 400 + (underTricks - 1) * 600
			else:
				score -= 200 + (underTricks - 1) * 400
				if underTricks > 3:
					score -= (underTricks - 3) * 200
		else:
			if vulnerable:
				score -= 100 + (underTricks - 1) * 100
			else:
				score -= 50 + (underTricks - 1) * 50

	return score


def scoreRubber(self, result):
	pass  # TODO: implement.
