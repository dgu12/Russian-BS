# -*- coding: utf-8 -*-
"""
Created on Tue May 17 19:26:36 2016

@author: giraffe
"""

import random
from collections import Counter

"""
Structure of this file:
global variables
Player classes
helper functions
playGame function (runs one game between two players)
main function (runs many games between given AI's)

Set verbose to True for debugging help, but definitely not recommended
when running more than one game at a time.
"""

verbose = False

"""
Cards will primarily be represented as integers 1..52 throughout, but
other representations will be included for debugging convenience.
"""
deck = range(0, 52)
ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
         "Nine", "Ten", "Jack", "Queen", "King"]
suits = ["Spades", "Clubs", "Diamonds", "Hearts"]
cardNumToName = {n : ranks[n % 13] + " of " + suits[n / 13] for n in deck}
cardNumToRankName = {n : ranks[n % 13] for n in deck}
cardNumToSuitName = {n : suits[n / 13] for n in deck}

dcards = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13",
          "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13",
          "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13",
          "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13"]

"""
topOfStack and bottomOfStack are global for convenience. No peeking from within
a Player class!
"""
topOfStack = set()
bottomOfStack = set()



"""
matchHistory will be a list of tuples, one per turn. There will be two types
of tuples:
(BS/Believe, callFailure/Success, [list of cards revealed], turn)
(rankClaimed, numberOfCards, turn)
Thus, matchHistory will contain all public information.
"""
matchHistory = []

"""
PLAYER CLASS-----------------------------------------------------------------//
The base player class, from which all derived classes supply a chooseMove()
function.
"""

class Player:
    """
    Base class for all players. All players by default represent their hand as a set
    where each card is represented by an integer 0..51.
    
    Further, each player has to be able to gain cards when the game forces
    that player to pick up cards. Each Player instance must also include
    a chooseMove(self) function. Note that since the match history is global,
    players don't need to be passed it in order to make a move.
    
    Each player knows its pid(turn).
    """
    
    def __init__(self):
        """
        Give self an empty hand.
        """
        self.hand = set()
    
    def gainCards(self, cards):
        """
        Union the player's hand with the given cards.
        """
        self.hand |= cards
    
    def setTurn(self, turn):
        """
        Sets this players turn number, i.e. its pid.
        """
        self.turn = turn
    
    def getHand(self):
        """
        Returns a set-of-integers representation of the player's hand.
        MUST BE OVERRIDDEN IF USING A DIFFERENT INTERNAL REPRESENTATION!
        """
        return self.hand
        
"""
DERIVED CLASSES--------------------------------------------------------------//
These classes inherit from the Player class and supply a chooseMove() function
and possibly other helper functions as well.
"""

class RandomAI1Player(Player):
    """
    Class for a trash random AI player. If stack is empty, plays one card
    randomly selected from its hand, and always tells the truth.
    Otherwise, flips a coin to call Believe or BS.
    """
    
    def chooseMove(self):
        """
        If stack is empty, plays one card randomly selected from its hand, 
        and always tells the truth.
        Otherwise, flips a coin to decide between calling believe and bs.
        """
        if isStackEmpty():
            c = random.choice(list(self.hand))
            self.hand -= set([c])
            return (c % 13, set([c]))
        else:
            return random.choice(["Believe", "BS"])
     

class RandomAI2Player(Player):
    """
    Class for a trash random AI player. If stack is empty, plays one card
    randomly selected from its hand, flipping a coin to decide whether or not
    to lie.
    Otherwise, flips a coin to decide between calling believe and bs.
    """
    
    def chooseMove(self):
        """
        If stack is empty, plays one card randomly selected from its hand, 
        flipping a coin to decide whether or not to lie.
        Otherwise, flips a coin to decide between calling believe and bs.
        """
        if isStackEmpty():
            c = random.choice(list(self.hand))
            self.hand -= set([c])
            if random.random() > .5:
                return (c % 13, set([c])) # Tell the truth.
            else:
                return (random.choice(list(set(range(0, 13)) - set([c]))), set([c])) # Lie.
        else:
            return random.choice(["Believe", "BS"])
    
    
class NaivePlayer(Player):
    """
    Class for a very naive player. Represents the surprisingly common newbie
    strategy of play as many cards as possible without lying, and if you can't
    play any, call believe or bs based on past experience with the two.
    """
    
    def chooseMove(self):         
        """
        If stack is empty, plays all of the most common rank that it can.
        Otherwise, tries to play cards of the same rank, but won't lie.
        If unable to, goes with the bs/believe option that it has had most
        success with in the past.
        """
        if isStackEmpty():
            # Play as many cards as possible without lying.
            cardsByRank = [card % 13 for card in self.hand]
            mostCommonRank = max(set(cardsByRank), key=cardsByRank.count)
            cardsToPlay = set([c for c in self.hand if c % 13 == mostCommonRank])
            self.hand -= cardsToPlay
            return (mostCommonRank, cardsToPlay)
            
        else:
            prevRank = matchHistory[-1][0]
            cardsOfPrevRankInHand = set([c for c in self.hand if c % 13 == prevRank])
            if cardsOfPrevRankInHand:
                return (prevRank, cardsOfPrevRankInHand)
            else:
                ''' Now we've gotta call bs or believe. We will examine our past
                bs/believe calls and flip a weighted coin to decide what to do.'''
                pastBelieveResults = [move[1] for move in matchHistory 
                        if move[-1] == self.turn and move[0] == "Believe"]
                pastBSResults = [move[1] for move in matchHistory 
                        if move[-1] == self.turn and move[0] == "BS"]
                if not pastBelieveResults:
                    # Go ahead and explore.
                    return "Believe"
                elif not pastBSResults:
                    return "BS"
                else:
                    # We have past results. Go with the more promising option.
                    believePercentCorrect = pastBelieveResults.count(True) / len(pastBelieveResults)
                    bsPercentCorrect = pastBSResults.count(True) / len(pastBSResults)
                    return "Believe" if believePercentCorrect > bsPercentCorrect else "BS"


class HumanPlayer(Player):
    """
    Class for a human player. Prompts user for input to make a move.
    Kind of clunky to use, but oh well.
    """
    def chooseMove(self):
        """
        Requests a move from a human. Moves must be entered in one of 
        two formats:
        bs OR believe
        claimedRank card1 card2 card3...
        Where the cards are entered as e.g. "S1 D12 C5 D7"
        """
        moveString = raw_input("Enter a move: ")
        if moveString.lower() == "believe" or moveString.lower() == "bl":
            return "Believe"
        elif moveString.lower() == "bs":
            return "BS"
        else:
            try:
                # Try to parse as a claimed rank followed by actual cards.
                claimedRank = int(moveString.split()[0]) - 1
                actualCards = moveString.split()[1:]
                actualCards = set([dcards.index(card) for card in actualCards])
                if not actualCards.issubset(self.hand):
                    raise Exception()
                self.hand -= actualCards
                return (claimedRank, actualCards)
            except:
                print "Idiot. You gave me an invalid input. Try again."
                return self.chooseMove()

"""
HELPER FUNCTIONS for running the game----------------------------------------//
"""

def isValid(move):
    """
    Checks the validity of a move. In particular, checks that BS/Believes
    aren't called on an empty board and the claimed rank is the same
    as the previous claimed rank. Returns True for valid, False for invalid.
    """
    # This is here to deal with the special case of the first round.
    if len(matchHistory) != 0:
        lastMove = matchHistory[-1][0]
    else:
        return True if move != "BS" and move != "Believe" else False
        
    
    if move == "BS" or move == "Believe":
        if lastMove == "BS" or lastMove == "Believe":
            return False
    else:
        if lastMove != "BS" and lastMove != "Believe":
            if move[0] != lastMove: # If a differing rank was played...
                return False
    return True
        

def isCallCorrect(call, topOfStack):
    """
    Checks if a call is correct. Takes either "Believe" or "BS" and returns
    True if the call is correct and False is the call isn't correct.
    """
    lastMove = matchHistory[-1]
    for card in topOfStack:
        if card % 13 != lastMove[0]:
            # One wrong card indicates an incorrect believe or a correct bs.
            return False if call == "Believe" else True
    # All cards were as claimed. Believe is correct, bs is incorrect.
    return True if call == "Believe" else False

  
def printMove(pid, move):
    """
    Prints a player's move to the terminal. Used when verbose is True.
    """
    if move == "Believe":
        print "Player " + str(pid) + " called Believe!"
    elif move == "BS":
        print "Player " + str(pid) + " called BS!"
    else:
        print "Player " + str(pid) + " claims to have played " + str(len(move[1])) + " " + ranks[move[0]] + "\'s."
        
        
def getStartingHands(numPlayers):
    """
    Produces a list of numPlayers starting hands. Each element of the list
    is a set representing a hand. The union of all hands is the deck.
    !!!
    This function only works for numPlayers that evenly divides 52 because
    I'm too lazy to make it better.
    !!!
    """
    deck = range(0, 52)
    random.shuffle(deck)
    handSize = 52 / numPlayers
    hands = [set(deck[i*handSize : (i + 1)*handSize]) for i in range(numPlayers)]
    return hands
    
    
def isStackEmpty():
    """
    Returns whether or not there are any cards in the stack.
    """
    return len(topOfStack) == 0
    
"""
playGame()-------------------------------------------------------------------//
Actually simulates the game.
"""
      
def playGame(players):
    """
    Plays a game between the provided players. Returns a list of the class 
    names of the winning player(s). 
    Note that in this implementation, a game ends as soon as someone wins.
    "If you aint first, you're last."
    """
    # Initialize variables for this game.
    global matchHistory, topOfStack, bottomOfStack
    matchHistory = []
    hands = getStartingHands(len(players))
    for i in range(len(players)):
        players[i].gainCards(hands[i])
        players[i].setTurn(i)
    
    bottomOfStack = set() # all cards before the most recently played cards
    topOfStack = set() # i.e. the most recently played cards
    turn = 0
    
    # Keep playing indefinitely. Break only if someone wins.
    while True:
        player = players[turn]
        
        if verbose:
            print 'Player ' + str((turn + 1)) + '\'s hand is:'
            print [dcards[c] for c in sorted(list(player.getHand()))]
        
        # Get and check move.
        move = player.chooseMove()
        if not isValid(move):
            raise Exception("We got the following invalid move: " + str(move))
        if verbose:
            printMove(players.index(player) + 1, move)
        
        # Player didn't make a call. Just play their cards and record it.
        if move != "BS" and move != "Believe":
            matchHistory.append((move[0], len(move[1]), turn))
            bottomOfStack |= topOfStack
            topOfStack = move[1] # Cards are added to top of stack.
            
        else: # Player made a call.
            if isCallCorrect(move, topOfStack):
                if move == "Believe":
                    # Record move, clear stack, and give player an extra turn.
                    if verbose:
                        print "Correct Believe call!"
                    matchHistory.append((move, True, topOfStack, turn))
                    bottomOfStack = set()
                    topOfStack = set()
                    turn -= 1
                elif move == "BS":
                    # Record move, give stack to last player, and give extra turn.
                    if verbose:
                        print "Correct BS call!"
                    matchHistory.append((move, True, topOfStack, turn))
                    prevPlayer = players[(turn - 1) % len(players)]
                    prevPlayer.gainCards(bottomOfStack)
                    prevPlayer.gainCards(topOfStack)
                    bottomOfStack = set()
                    topOfStack = set()
                    turn -= 1
            else: # Call wasn't correct.
                if verbose:
                    print "Incorrect call!"
                matchHistory.append((move, False, topOfStack))
                player.gainCards(bottomOfStack)
                player.gainCards(topOfStack)
                bottomOfStack = set()
                topOfStack = set()
            
            
            ''' We always check for a winner after a BS/Believe call, as this
            is the only time someone can win. '''
            winners = [p.__class__.__name__ for p in players if not p.getHand()]
            if winners:
                if verbose:
                    print "Players of the following types won this match:"
                    for winner in winners:
                        print winner
                    
                return winners
        
        # Done processing move; update whose turn it is.        
        turn = (turn + 1) % len(players)
    
    
    
if __name__ == '__main__':
    num_matches = 1000
    winners = []
    for i in range(num_matches):
        p1 = RandomAI1Player()
        p2 = RandomAI2Player()
        p3 = RandomAI2Player()
        p4 = NaivePlayer()
        players = [p1, p2, p3, p4]
        random.shuffle(players)
        winners += playGame(players)
    print "We played " + str(num_matches) + " matches. Here's each AI's win count:"
    print dict(Counter(winners))
    


















