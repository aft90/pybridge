# Arranged by relative value.


class CallType:
	Pass = 'pass'; Bid = 'bid'; Double = 'double'
	CallTypes = [Pass, Bid, Double]


class Denomination:
	Club = 'club'; Diamond = 'diamond'; Heart = 'heart'; Spade = 'spade'; NoTrump = 'notrump'
	Denominations = [Club, Diamond, Heart, Spade, NoTrump]


class Rank:
	Two = 'two'; Three = 'three'; Four = 'four'; Five = 'five'; Six = 'six'
	Seven = 'seven'; Eight = 'eight'; Nine = 'nine'; Ten = 'ten'
	Jack = 'jack'; Queen = 'queen'; King = 'king'; Ace = 'ace'
	Ranks = [Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King, Ace]


class Seat:
	North = 'north'; South = 'south'; East = 'east'; West = 'west'
	Seats = [North, East, South, West]  # Clockwise.


class Suit:
	Club = 'club'; Diamond = 'diamond'; Heart = 'heart'; Spade = 'spade'
	Suits = [Club, Diamond, Heart, Spade]
