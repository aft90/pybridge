class Scoring:
	"""
	Base scoring class.
	"""
	
	def __init__(self):
		self.contractLevel = 0
		self.trumpSuit = 'c'
		self.tricksMade = 0
		self.declarer = 'n'
		self.doubled = False
		self.redoubled = False
		self.vulnerable = False

class ScoreDuplicate(Scoring):
	"""
	Scoring algorithm for duplicate bridge.
	"""

	def score(self):
		theScore = 0
		if self.tricksMade >= self.contractLevel + 6:
			# Contract fulfilled.
			
			# Calculate scores for tricks bid and made.
			if self.trumpSuit == 'c' or self.trumpSuit == 'd':
				# Clubs and Diamonds score 20 for each odd trick.
				theScore += self.contractLevel * 20
			else:
				# Hearts, Spades and NT score 30 for each odd trick.
				theScore += self.contractLevel * 30
				if self.trumpSuit == 'n':
					# For NT, add a 10 point bonus.
					theScore += 10
			
			# Calculate scores for doubles.
			if self.doubled:
				# Multiply score by 2 for each doubled odd trick.
				theScore *= 2
			elif self.redoubled:
				# Multiply score by 4 for each redoubled odd trick.
				theScore *= 4
			
			# Calculate premium scores.
			if theScore >= 100:
				if self.vulnerable:
					# Game, vulnerable.
					theScore += 500
				else:
					# Game, not vulnerable.
					theScore += 300
				if self.contractLevel == 7:
					if self.vulnerable:
						# Grand slam, vulnerable.
						theScore += 1500
					else:
						# Grand slam, not vulnerable.
						theScore += 1000
				elif self.contractLevel == 6:
					if self.vulnerable:
						# Small slam, vulnerable.
						theScore += 750
					else:
						# Small slam, not vulnerable.
						theScore += 500
				
			else:
				# Any part score.
				theScore += 50
			if self.doubled:
				# Contract doubled, "for the insult".
				theScore += 50
			elif self.redoubled:
				# Contract redoubled, "for the insult".
				theScore += 100
			
			# Calculate scores for overtricks.
			overTricks = self.tricksMade - self.contractLevel - 6
			if overTricks > 0:
				if self.doubled:
					if self.vulnerable:
						# Score 200 for each doubled and vulnerable overtrick.
						theScore += overTricks * 200
					else:
						# Score 100 for each doubled and not vulnerable overtrick.
						theScore += overTricks * 100
				elif self.redoubled:
					if self.vulnerable:
						# Score 400 for each redoubled and vulnerable overtrick.
						theScore += overTricks * 400
					else:
						theScore += overTricks * 200
				else:
					if self.trumpSuit == 'c' or self.trumpSuit == 'd':
						# Clubs and Diamonds score 20 for each undoubled overtrick.
						theScore += overTricks * 20
					else:
						# Hearts, Spades and NT score 30 for each undoubled overtrick.
						theScore += overTricks * 30
		
		else:
			# Contract not fulfilled.
			underTricks = self.contractLevel + 6 - self.tricksMade
			if self.doubled:
				if self.vulnerable:
					# Score 200 for the first doubled and vulnerable undertrick
					# and 300 for all other undertricks.
					theScore -= 200 + (underTricks - 1) * 300
				else:
					# Score 100 for the first doubled and non-vulnerable
					# undertrick and 300 for all other undertricks.
					# Score 100 extra for undertricks.

					theScore -= 100 + (underTricks - 1) * 200
					if underTricks > 3:
						theScore -= (underTricks - 3) * 100
			elif self.redoubled:
				if self.vulnerable:
					theScore -= 400 + (underTricks - 1) * 600
				else:
					theScore -= 200 + (underTricks - 1) * 400
					if underTricks > 3:
						theScore -= (underTricks - 3) * 200
			else:
				if self.vulnerable:
					theScore -= 100 + (underTricks - 1) * 100
				else:
					theScore -= 50 + (underTricks - 1) * 50
				
		# Return score
		return theScore
			
class ScoreRubber(Scoring):
	"""
	Scoring algorithm for rubber bridge.
	"""

	def ScoreRubber(self):
		pass
