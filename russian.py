# Daniel Gu

'''
This program allows the user to play a the game Russian BS versus an AI
opponent.
'''

import sys
import random

# Define some useful constants.
BELIEVE = 0
BS = 1

# Global list of ranks.
ranks = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
# Global list of aliases for cards.
dcards = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13",
          "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13",
          "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13",
          "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13",]
cstr = [str(i) for i in range(1, 53)]

# Make a dictionary of cards. We associate each card in the standard deck with
# an integer in [0, 51] according to the following mapping:
# 0 - 12: Ace - King of spades
# 13 - 25: Ace - King of clubs
# 26 - 38: Ace - King of diamonds
# 39 - 51: Ace - King of hearts
# In this mapping, the residue mod 13 gives the rank of the card (with jack as
# 11, queen as 12, king as 13), and the integer division by 13 gives the suit
# (0 is spades, 1 is clubs, 2 is diamonds, and 3 is hearts). Furthermore, the
# bottom "half" consists of black cards, whereas the top "half" consists of
# black cards.
def makeCards():
	carddict = dict()
	for i in range(13):
		key1 = "S" + str(i)
		key2 = "C" + str(i)
		key3 = "D" + str(i)
		key4 = "H" + str(i)
		carddict[key1] = i
		carddict[key2] = i + 13
		carddict[key3] = i + 26
		carddict[key4] = i + 39
	return carddict

# PLAYER CLASS---------------------------------------------------------------//

class Player:
	'''Class for a player in the game Russian BS'''

	# Member variables:
	#    pid        -> the player ID as assigned by the game.
	#    isAI       -> flag determining whether player is AI or not.
	#    carddict   -> a dictionary for translating cards.
	#    state      -> dictionary holding state of game of other players
	#    game_state -> holds the state of the current round
	#    game_hist  -> holds the entire history of the game so far.
	#    nplayers   -> number of players

	# Takes a list of cards and a flag for whether the player is AI or not.
	def __init__(self, PID, pcards, AI, nplayers):
		self.pid = PID
		self.AI = AI
		self.carddict = makeCards()
		# Holds the knowledge of all players' cards.
		self.state = dict()
		for i in range(nplayers):
			self.state[i] = []
		self.state[PID] = pcards
		self.state["out"] = []
		self.game_state = []
		self.game_hist = []
		self.nplayers = nplayers

	# AI FUNCTIONS-----------------------------------------------------------\\
	# TODO: Eventually change this to a class-inheritance style system.

	# Basic AI which always plays a valid move if it goes first; otherwise it
	# randomly picks between "believe" and "BS".
	def moveAI(self, first = False):
		random.seed()
		if first:
			l = []
			# Pick a random card and declare it correctly.
			card = random.choice(self.getCards())
			l.append(card)
			# Get the rank of the card.
			rank = card % 13
			# Remove the card from our hand.
			self.removeCards(self.pid, l)
			return (rank, 1, card)
		else:
			# Return BELIEVE or BS uniformly at random.
			return random.randint(0, 1)

	# ACCESSORS--------------------------------------------------------------\\

	# Accessor for the PID of the player.
	def getPID(self):
		return self.pid

	# Accessor which returns the list of cards held by the player.
	def getCards(self):
		return self.state[self.pid]

	# Get the cards which are NOT held by the player.
	def getOtherCards(self):
		other = []
		for i in range(52):
			if i not in self.state[self.pid]:
				other.append(i)
		return other

	# Accessors which returns whether the player is an AI/
	def isAI(self):
		return self.AI

	# MUTATORS---------------------------------------------------------------\\

	# Add cards in the numeric format.
	def addCards(self, pid, cards, cdict = False):
		if cdict:
			for card in cards:
				self.state[pid].append(self.carddict[card])
		else:
			self.state[pid] += cards

	def removeCards(self, pid, cards, cdict = False):
		if cdict:
			for card in cards:
				if self.carddict[card] in self.state[pid]:
					self.state[pid].remove(self.carddict[card])
		else:
			for card in cards:
				if card in self.state[pid]:
					self.state[pid].remove(card)

	# Get the game state.
	def getGameState(self, state):
		self.game_state = state

	# Get the game history, which is supposed to hold previous opponent
	# decisions.
	def getGameHistory(self, hist):
		self.game_hist.append(hist)

	# MOVE FUNCTIONS AND HELPERS---------------------------------------------\\

	def prompt(self, rank):
		print "The current rank is %s" % ranks[rank]
		is_card = raw_input("Play Cards?>> ")
		if is_card.strip() == "YES":
			dnum = raw_input("Declared Number>> ")
			actual = raw_input("Actual>> ")
			translated = actual.strip().split()
			while dnum not in cstr or int(dnum) != len(translated) or not self.isSubset(translated):
				print "Enter a proper subset of your cards."
				dnum = raw_input("Declared Number>> ")
				actual = raw_input("Actual>> ")
				translated = actual.strip().split()
			# Remove the cards we're playing.
			self.removeCards(self.pid, self.translate(actual))
			# Input should be 1-indexed rank.
			return (rank, int(dnum), self.translate(actual))
		elif is_card.strip() == "NO":
			action = raw_input("Action>> ")
			while action.strip() != BELIEVE and action.strip() != BS:
				print "Enter BELIEVE or BS"
				action = raw_input("Action>> ")
			if action.strip() == "BELIEVE":
				return BELIEVE
			else:
				return BS

	# Moves which are not "believe" or "BS" should be formatted as follows:
	# ([rank] [# of cards] [list of actual cards])
	# i.e. a 3-tuple of which the first element is the rank, second element is
	# the number of cards played, and the third is list of the actual card.
	def playMove(self, first = False, rank = None):
		if first:
			if self.AI:
				move = self.moveAI(first = True)
			else:
				self.printCards()
				drank = raw_input("Declared Rank>> ")
				dnum = raw_input("Declared Number>> ")
				actual = raw_input("Actual>> ")
				translated = actual.strip().split()
				while drank not in ranks or dnum not in cstr or int(dnum) != len(translated) or not self.isSubset(translated):
					print "Enter a proper rank and a subset of your cards."
					drank = raw_input("Declared Rank>> ")
					dnum = raw_input("Declared Number")
					actual = raw_input("Actual>> ")
					translated = actual.strip().split()
				# Remove the cards we've played.
				self.removeCards(self.pid, self.translate(actual))
				# Input should be 1-indexed rank.
				move = (self.convertRank(drank), int(dnum), self.translate(actual))
		else:
			if not self.AI and rank != None:
				self.printCards()
				# Get a move from the command line.
				move = self.prompt(rank)
			else:
				move = self.moveAI()
		return move

	# Uses the global ranks list to convert a rank to its internal
	# representation (i.e., in range(13)).
	def convertRank(self, rank):
		return ranks.index(rank)

	# Checks to see whether the actual move is a playable move, i.e. a subset
	# of the player's current cards. Looks at cards from the command line.
	def isSubset(self, cardlist):
		# Copy our list so we don't have to deal with aliasing issues.
		cards = [i for i in self.getCards()]
		for card in cardlist:
			if card in self.carddict.keys():
				card = self.carddict[card]
				if card in cards:
					cards.remove(card)
				else:
					return False
			else:
				return False
		return True

	# Converts a list of cards from external format to internal format.
	def convert(self, cardlist):
		converted = []
		for card in cardlist:
			converted.append(self.carddict[card])
		return converted

	# Parses an entered list of cards into internal format.
	def translate(self, movestr):
		temp = movestr.strip().split()
		cards = [self.carddict[i] for i in temp]
		return cards

	# Prints the cards in external format.
	def printCards(self):
		cards = self.getCards()
		print "Player %d's cards: " % self.pid
		for card in cards:
			name = ""
			suit = card / 13
			rank = (card % 13) + 1
			if suit == 0:
				name = "S" + str(rank)
			elif suit == 1:
				name = "C" + str(rank)
			elif suit == 2:
				name = "D" + str(rank)
			else:
				name = "H" + str(rank)
			print "%s" % name

# RUSSIANBS CLASS------------------------------------------------------------//

class RussianBS:
	'''Runs the game of Russian BS.'''

	# Member variables:
	# nplayers    -> The number of players in the game
	# player_list -> A list holding every player in the game
	# out         -> Holds cards which are out of the game.
	# round       -> Holds the state of the current round.
	# won         -> Integer holding who won the game (or -1)
	# turn        -> The PID of the player whose turn it is

	# AI is expected to be a list of booleans of length num_players
	def __init__(self, num_players, AI):
		self.nplayers = num_players
		self.player_list = range(num_players)
		# Randomly deal cards to each player.
		random.seed()
		# Each player gets a least base cards:
		quotient = 52 / num_players # Integer division.
		remainder = 52 % num_players
		pool = range(52)
		for i in range(num_players):
			if remainder > 0:
				cards = random.sample(pool, quotient + 1)
				remainder -= 1
			else:
				cards = random.sample(pool, quotient)
			# Get rid of the cards we've already assigned.
			for card in cards:
				pool.remove(card)
			# Create our player
			self.player_list[i] = Player(i, cards, AI[i], num_players)
		# List of cards which are out of the game.
		self.out = []
		self.round = []
		self.won = -1
		self.turn = 0

	# Runs the game.
	def runGame(self):
		while self.won == -1:
			self.updateRound()
		print "Player %d has won!" % self.won

	# Runs each round of the game. Moves are kept as a tuple of
	# the list of cards declared, and the list of cards played.
	# self.round keeps the PID of the player that made the move followed by
	# the actual move.
	#
	# All cards here should be in their internal representation (i.e., in
	# range(52)).
	def updateRound(self):
		ended = False
		correct = False
		first = True
		rank = None
		total_cards = 0
		while not ended:
			for player in self.player_list:
				print "Player %d has %d cards." % (player.getPID(), len(player.getCards()))
			print "Player %d's turn." % self.turn
			# We already check for valid moves in playerMove() member function.
			move = self.player_list[self.turn].playMove(first = first, rank = rank)
			first = False
			if rank == None:
				rank = move[0] # The rank is held in the first coordinate.
			if (move == BELIEVE or move == BS) and self.round != []:
				# The last player didn't lie.
				if self.isEqual(self.round[-1]):
					if move == BELIEVE:
						# If we correctly believe, the cards exit the game.
						all_cards = []
						for tup in self.round:
							current_pid, current_cards = tup[0], tup[3]
							all_cards += current_cards
							# Each player gains the information that the cards
							# they played go out.
							self.player_list[current_pid].addCards("out", current_cards)
						self.out += all_cards
						correct = True
					elif move == BS:
						# We guessed wrong, so the current player gets all of the cards.
						# In addition, all of the other players learn that this player
						# gets all of the cards.
						all_cards = []
						for i in range(len(self.round)):
							all_cards += self.round[i][3]
						# Now give the cards to the current player, and information
						# to the other players.
						for player in self.player_list:
							player.addCards(self.turn, all_cards)
				# The last player did lie.
				else:
					if move == BELIEVE:
						# We guessed wrong, so the current player gets all of the cards.
						# In addition, all of the other players learn that this player
						# gets all of the cards.
						all_cards = []
						for i in range(len(self.round)):
							all_cards += self.round[i][3]
						# Now give the cards to the current player, and information
						# to the other players.
						for player in self.player_list:
							player.addCards(self.turn, all_cards)
					elif move == BS:
						# We guessed right, so the previous player takes all of the
						# cards and each player learns the cards played.
						all_cards = []
						for i in range(len(self.round)):
							all_cards += self.round[i][3]
						# Now give the cards to the previous player, and information
						# to the other players.
						for player in self.player_list:
							player.addCards(self.turn - 1, all_cards)
						correct = True
				# Now reset everything for the next round and end the turn.
				# Update the histories for each player.
				for player in self.player_list:
					player.getGameHistory(self.round)
				# Reset self.round.
				self.round = []
				if not correct:
					self.turn = (self.turn + 1) % self.nplayers
				self.won = self.hasWon()
				ended = True
			# Otherwise, add the move the our internal state.
			else:
				(rank, num, cards) = move
				print "Player %d has played %d cards of rank %s" % (self.turn, num, ranks[rank])
				tup = (self.turn, rank, num, cards)
				self.round.append(tup)
				self.turn = (self.turn + 1) % self.nplayers

	# A player has won if they have no cards at the end of their turn.
	def hasWon(self):
		for player in self.player_list:
			if len(player.getCards()) == 0:
				return player.getPID()
		return -1

	# Given a move, determines whether the player lied while making the move.
	def isEqual(self, move):
		(PID, rank, number, cards) = move
		if len(cards) == number:
			for card in cards:
				if card % 13 != rank:
					return False
			return True
		else:
			return False

# GAME FUNCTIONS-------------------------------------------------------------//

# Runs a game of RussianBS, using the classes defined above.
def playGame():
	# Get the number of players
	nplayers = int(raw_input("Number of players>> "))
	nAI = int(raw_input("Number of AI players>> "))
	AI = range(nplayers)
	for i in range(nplayers):
		if i < nAI:
			AI[i] = True
		else:
			AI[i] = False
	game = RussianBS(nplayers, AI)
	game.runGame()
	q = raw_input("Quit?>> ")
	if q == "Y":
		return True
	else:
		return False

# MAIN-----------------------------------------------------------------------//

if __name__ == '__main__':
	done = False
	while not done:
		done = playGame()
		
