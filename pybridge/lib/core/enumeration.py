class Denomination:
	Club = 'club'; Diamond = 'diamond'; Heart = 'heart'; Spade = 'spade'; NoTrump = 'notrump'
	# Club, Diamond, Heart, Spade, NoTrump = range(5)
	Denominations = [Club, Diamond, Heart, Spade, NoTrump]

class Rank:
	Two = 'two'; Three = 'three'; Four = 'four'; Five = 'five'; Six = 'six'
	Seven = 'seven'; Eight = 'eight'; Nine = 'nine'; Ten = 'ten'
	Jack = 'jack'; Queen = 'queen'; King = 'king'; Ace = 'ace'
	# Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King, Ace = range(2, 15)
	Ranks = [Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King, Ace]

class Suit:
	Club = 'club'; Diamond = 'diamond'; Heart = 'heart'; Spade = 'spade'
	# Club, Diamond, Heart, Spade = range(4)
	Suits = [Club, Diamond, Heart, Spade]

class Seat:
	North = 'north'; South = 'south'; East = 'east'; West = 'west'
	# North, South, East, West = range(4)
	Seats = [North, South, East, West]
