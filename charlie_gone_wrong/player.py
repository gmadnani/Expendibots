import heapq
from copy import deepcopy, copy
import math

#Global Constants
STACK=0
COORDINATES=1
X=0
Y=1
OBJECT=2
MAX_NODE_BUDGET=115000
MOVE_COORDINATES=[(0,1), (0,-1), (1,0), (-1,0)]
BASE_COEFFICIENT=0.5 #was 1.48
MIN_LOG=2
MAX_DEPTH_CAP=4
DEPTH_CURB_FACTOR=0.8
MAX_SCORE=999999999

#Values for determining the score of our heuristic
CENTRE_VALUE=8
PIECE_VALUE=300
DISTANCE_VALUE=25  #At most is multiplied by a factor of 2.3
ATTACK_TILL_TURN=26

class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your
        program will play as (White or Black). The value will be one of the
        strings "white" or "black" correspondingly.
        """
        # TODO: Set up state representation.

        #Initialise the starting positions for the black and white tiles
        self.data = {}
        white_tiles={}
        black_tiles={}

        for y in range(0,2):
            for x in range(0,8):
                #Skip the values of 2 and 5
                if(((x+1) % 3)!=0):
                    white_tiles[(x,y)]=1
                    black_tiles[(x,7-y)]=1

        self.data["white"]=white_tiles
        self.data["black"]=black_tiles
        self.no_of_coins={"white": 12, "black": 12}
        self.parent = None
        self.score = None
        self.depth = 0
        self.move=None
        self.to_make_move=None
        self.playing_as = colour
        self.turn_count=0
        self.history=[]
        if colour == "white":
            self.opponent="black"
        else:
            self.opponent="white"


    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        # TODO: Decide what action to take, and return it

        if self.turn_count>1:
            self.to_make_move=self.playing_as
            decision=minimax(self)
            return tuple(decision)
        # Hardcoded starting moves, just the first turn or two
        else:
            # If white, first move should always be to make a double stack in 
            # the middle. This gives us the best range of options to work with.
            if self.playing_as=="white":
                return tuple(["MOVE",1,(3,1),(4,1)])
            else:
                # We are playing as black. A smart AI would make a stack of 2 on their
                # front lines. We should inverse their action in the corresponding group
                # for our first move.

                # First find the opponents stack
                for coin in self.data[self.opponent]:
                    if self.data[self.opponent][coin]==2 and coin[Y]==1:
                        if not ((coin[X]+1 ==3) or (coin[X]+1 == 5) or (coin[X]+1 == 8)):
                            return tuple(["MOVE",1,(coin[X],6),(coin[X]+1,6)])
                        else:
                            return tuple(["MOVE",1,(coin[X],6),(coin[X]-1,6)])
                # Otherwise, the AI has not made such an important move, 
                # make double stack in the middle
                return tuple(["MOVE",1,(3,6),(4,6)])



    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action 
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
        # TODO: Update state representation in response to action.

        #Save move to self
        self.move=action

        #If action is MOVE then update the coins accordingly
        if(action[0]=="MOVE"):

            #Subtract n from starting coin coordinates
            self.data[colour][action[2]]-=action[1]
            
            #If there nothing left in the stack, remove it
            if(self.data[colour][action[2]]<=0):
                del self.data[colour][action[2]]

            #Check if there is already a coin at target destination
            if(action[3] in self.data[colour]):
                #Update the amount in the stack
                self.data[colour][action[3]]+=action[1]

            #Else, make the new coin appear at destination
            else:
                self.data[colour][action[3]]=action[1]

            # Update move history
            self.history.insert(0,action)
            # Keep the size of history to a max of 20
            while len(self.history)>20:
                del self.history[-1]
        

        #Else it is BOOM, do this
        else:
            check_boom(action, self)
            # Booms cannot be repeated, restart history.
            self.history=[]

        self.turn_count+=1


##### MINIMAX AB PRUNING FUNCTIONS #####

def minimax(node_state):
# Main minimax function, takes a given game_state as an input and returns the best possible move 

    #Initialise variables

    # sets the depth level, depending on amount of coins left
    budget_depth=depth_calc(node_state)

    # Checks the history of moves so that we don't get stuck in a repetitive loop
    rep_list=rep_check(node_state.history)
    
    current_depth = budget_depth+1
    best_state = None
    node_state2 = deepcopy(node_state)
    switch_turn(node_state2)
    node_state2.depth-=1

    while not best_state and current_depth > 0:
        current_depth -= 1
        # Get the best move possible
        best_state = max_move(node_state2,[float('-inf'),float('inf')],budget_depth,rep_list)[0]

    return best_state.move

def mm_best_move(node_state, par_bounds,budget_depth,rep_list):
# Is the function that actually decides the best move

    # Update depth and turn for the state
    switch_turn(node_state)
    node_state.depth+=1

    #Check if it's game over or we've reached max depth
    if game_over(node_state) or (node_state.depth>=(budget_depth)):
        return (node_state,heuristic_eval(node_state,budget_depth,rep_list))

    #Initialise variables for minimax
    best_state=ExamplePlayer(node_state.playing_as)
    best_state.score=node_state.score

    #Initialise variables for ab pruning
    bounds=[float('-inf'),float('inf')]

    ### If it's a MaxNode ###
    if node_state.score == float('-inf'):

        # Generate a list of all possible moves
        moves_list=generate_moves(node_state)
        # Iterate through those moves to assess scores and make depth of tree
        for move in moves_list:

            # Make a new node and update it with the move info
            new_node=deepcopy(node_state)
            new_node.update(node_state.to_make_move,move)
            new_node.parent=node_state
            new_node.score = min_move(new_node,bounds,budget_depth,rep_list)[1]
            # Update the best score if necessary
            if new_node.score > best_state.score:
                best_state = new_node

            if best_state.score >= par_bounds[1]:
                return (best_state,best_state.score)

            if best_state.score > bounds[0]:
                bounds[0]=best_state.score

    ### If it's a MinNode ###
    elif node_state.score == float('inf'):
        # Generate a list of all possible moves
        moves_list=generate_moves(node_state)
        # Iterate through those moves to assess scores and make depth of tree
        for move in moves_list:
            new_node=deepcopy(node_state)
            new_node.update(node_state.to_make_move,move)
            new_node.parent=node_state
            new_node.score = max_move(new_node,bounds,budget_depth,rep_list)[1]
            # Update the best score if necessary
            if new_node.score < best_state.score:
                best_state = new_node
                bounds[1]=best_state.score

            if best_state.score <= par_bounds[0]:
                return (best_state,best_state.score)

            if best_state.score < bounds[1]:
                bounds[1]=best_state.score

    else:
        print("Shouldn't have gotten here egghead. Eggy egglord of the eggs with an egghead of egg.")

    #If we get to this point then everything should be parfait.
    return best_state, best_state.score

def min_move(min_node_state, bounds, budget_depth,rep_list):
# Calculates the best move from the opponents perspective

    min_node_state.score=float('inf')

    return mm_best_move(min_node_state, bounds,budget_depth,rep_list)

def max_move(max_node_state, bounds, budget_depth,rep_list):
# Calculates the best move from our perspective

    max_node_state.score=float('-inf')
    
    return mm_best_move(max_node_state, bounds,budget_depth,rep_list)

def heuristic_eval(node_state, budget_depth,rep_list):
# Is the function that decides the values for given states

    #Initialise Variables
    # Make a score modifier depending on whose turn it is
    if node_state.to_make_move==node_state.playing_as:
        score_mod=1
    else:
        score_mod=-1
    score=0.0

    # Dir intention changes functions to be compatible if we're playing as black
    move_intention=1
    opponent="black"
    if node_state.to_make_move=="black":
        opponent="white"
        move_intention=-1

    # Variable to decide to send coins towards opponents starting side
    turn_off_attack=1
    if node_state.turn_count > ATTACK_TILL_TURN:
        turn_off_attack=0

    # Check if we lost 
    if game_over(node_state) and game_over(node_state)==node_state.playing_as:
        return -MAX_SCORE
    # Make sure the move isn't being repeated. THIS ORDERING INBETWEEN THE LOSS
    # AND WIN STATE IS IMPORTANT. If we repeat then it won't be a win, but not losing
    # is more important as a repeat ends in a draw.
    if rep_list:
        node_copy=node_state
        while node_copy.parent!=None:
            if tuple(node_copy.move) in rep_list:
                return -MAX_SCORE/2*score_mod
            node_copy=node_copy.parent
    # If still game_over then we've won
    if game_over(node_state):
        return MAX_SCORE



    # Large score modifier if boom has pos effect for us
    # Difference in our coins
    diff_us=node_state.parent.no_of_coins[node_state.to_make_move]-node_state.no_of_coins[node_state.to_make_move]
    # Difference in their coins
    diff_opp=node_state.parent.no_of_coins[opponent]-node_state.no_of_coins[opponent]
    score+=(diff_opp-diff_us)*PIECE_VALUE
    # If there lose an equal amount but we have more pieces than them, we should take the trade
    # if there is not better option
    if (diff_opp-diff_us)==0 and node_state.no_of_coins[node_state.to_make_move]>node_state.no_of_coins[opponent]:
        score+=3/4*PIECE_VALUE


    # Let's use a distance between enemy coins and our coins as 
    # a small modifier to promote our coins movement towards the enemy
    score+=dist_heuristic(node_state, opponent)


    # Also add a small heuristic for controlling the center four 
    # squares of the board, or further depending on the stage of the game.
    for coin in node_state.data[node_state.to_make_move]:
        if ((abs(3.5-coin[X])<1 and abs(3.5-coin[Y])<1) or (coin[Y]*move_intention>3.5*move_intention)*turn_off_attack):
            score+=CENTRE_VALUE
            break


    # Another heuristic: if move a coin into a boomworthy state, with a definite win scenario
    if(budget_depth==2):
        if node_state.move[0]=="MOVE":
            score+=boomworth_state(node_state,opponent)


    return score*score_mod

##### END OF MINIMAX AB PRUNING FUNCTIONS #####


# Series of helper functions

def game_over(node_state):
# Returns the loser if the game has ended

    # If white has lost
    if node_state.no_of_coins["white"] == 0:
        return "white"
    # If black has lost
    elif node_state.no_of_coins["black"] == 0:
        return "black"
    else:
        return 0

def generate_moves(node_state):
# Generates moves for minimax to use

    coordinate_list = []

    if node_state.to_make_move == "white":
        opponent = "black"
        move_intention=1
    else:
        opponent = "white"
        move_intention=-1

    #for loop through tiles at our disposal
    for curr_tile in node_state.data[node_state.to_make_move]:
        #can move 1 to n amount of tiles
        for n in range (node_state.data[node_state.to_make_move][curr_tile], 0,-1):
            #can travel a distance of up to n spaces
            for stack_height in range(node_state.data[node_state.to_make_move][curr_tile], 0,-1):#for loop through move possibilities 
                #loop through move coordinates
                for move in MOVE_COORDINATES:
                    # Check the movement is allowed
                    move_to=(curr_tile[X]+move[X]*stack_height*move_intention, curr_tile[Y]+move[Y]*stack_height*move_intention)
                    if (tile_has_coin(move_to,node_state)!=opponent): #movement is not onto opponents coin
                        if(on_board(move_to)): #movement is on the board
                            #Add move to coordinate list. First move should be towards the opponents side of board
                            coordinate_list.append(["MOVE",n,curr_tile,move_to])

        # check the results of a boom. Only assesses if close to an enemy tile; efficiency improv
        if next_to_opponents_coin(curr_tile,node_state):
            #Add boom to coordinate list
            coordinate_list.insert(0,["BOOM",curr_tile])

    return coordinate_list

def switch_turn(node_state):
# Switches the turn of the attribute to_make_move

    if node_state.to_make_move == "white":
        node_state.to_make_move="black"
    else:
        node_state.to_make_move="white"
    return

def on_board(coords, **kwargs):
#checking if the coordinates are on the board

        return (coords[0]>=0 and coords[0]<=7 and coords[1]>=0 and coords[1]<=7)

def check_boom(action, node_state):
# Given coordinates of boom, removes coins from node_state

    #Find all the coins that need to be removed
    to_die=set()
    make_boom_set(action[1], node_state, to_die)

    remove_coins_from_state(node_state,to_die)

def make_boom_set(curr_coin, node_state, to_die, **kwargs):
#fills the set to_die with coins that will be removed if a boom happens at curr_coin

    #to_die needs to be a set, it allows this function to work recursively
    to_die.add(curr_coin)

    #Examine all coins
    for colour in node_state.data:
        for coin in node_state.data[colour]:

            # check if the coin is within range.
            dist=get_dist(coin,curr_coin)
            if(dist[X]<=1 and dist[Y]<=1):

                #To stop duplicates check if it's already in set.
                if(coin not in to_die):

                    #The coin is adjacent so call the make_boom_set function to recurse it, which in turn will add it to the set.
                    make_boom_set(coin, node_state, to_die)

    return

def remove_coins_from_state(node_state,to_die, **kwargs):
#Remove coins from the game state.
    temp=[]
    # Check if to_die is in dict - complexity should be quick
    for coin in to_die:
        for search_col in node_state.data:
            #If this coin is in the to_die set, remove it and update no_of_coins
            if coin in node_state.data[search_col]:
                node_state.no_of_coins[search_col]-=node_state.data[search_col][coin]
                del node_state.data[search_col][coin]

def next_to_opponents_coin(curr_coin, node_state, **kwargs):
#Function checks if there is an opponents coin within the boom radius

    if node_state.to_make_move == "white":
        opponent="black"
    else:
        opponent="white"

    #Examine opponents coins
    for coin in node_state.data[opponent]:

        # check if the opposing coin is within range.
        dist=get_dist(coin,curr_coin)
        if(dist[X]<=1 and dist[Y]<=1):
            return True

    return False

def tile_has_coin(coordinates, node_state, **kwargs):
# Checks if there is a coin at the coordinates given, and returns the colour of the coin if true

    # For loop through data
    for colour in node_state.data:
            if coordinates in node_state.data[colour]:
                return colour

    # Otherwise there is no coin on the tile
    return False

def get_dist(coin1, coin2):
#Returns a list of [X,Y] with the distance between the coins
    dist=[]
    dist.append(abs(coin1[X]-coin2[X])) 
    dist.append(abs(coin1[Y]-coin2[Y])) 
    return dist

def boomworth_state(node_state, opponent):
# Function heuristic that determines if a movement puts a tile in a good state to boom.

    move_coords = node_state.move[3]
    if next_to_opponents_coin(move_coords, node_state):

        # Check the effect of boom
        to_die=set()
        make_boom_set(move_coords, node_state, to_die)
        dir_adj=[]

        # Continue if we destroy more than just our coin and 2 opponent coins ## Update to include data about stacks
        if len(to_die) > 3:

            # Find if there is more than one opp. coin directly next to ours
            for coin in to_die:

                #Make sure the coin is the opponents
                for coin in node_state.data[opponent]:
                    continue

                dist=get_dist(move_coords,coin)
                good_choice=False

                if(dist[X]<=1 and dist[Y]<=1 and coin!=move_coords):
                    dir_adj.append(coin)

                # If there are 3 enemy coins near ours, we're guaranteed pos damage ## Update for stacks cons.
                if(len(dir_adj)>=2):
                    if (len(dir_adj)==2):
                        dist=get_dist(dir_adj[0],dir_adj[1])

                        # If they are not next to eachother
                        if(not (0 in dist and (1 in dist or 2 in dist))):
                            continue

                        #If here, we know there is a 0 in dist. If 2 then there is a space between the adj coins
                        if 2 in dist:
                            need_coin_at=(((dir_adj[0][X]+dir_adj[1][X])/2),((dir_adj[0][Y]+dir_adj[1][Y])/2))
                            for coin2 in to_die:
                                if coin2[COORDINATES]==need_coin_at:
                                    good_choice=True

                        #Otherwise we know with 0 and 1, we're in a good position
                        else:
                            good_choice=True
                    # If dir_adj > 2 then we're guaranteed a good position
                    else:
                        good_choice=True

                    if good_choice:
                        node_copy=deepcopy(node_state)
                        remove_coins_from_state(node_copy,to_die)

                        #If the change in coins is positive
                        change=(node_state.no_of_coins[opponent]-node_copy.no_of_coins[opponent])-(node_state.no_of_coins[node_state.to_make_move]-node_copy.no_of_coins[node_state.to_make_move])
                        if change>0:    
                            node_cop=node_state
                            while node_cop.parent!=None:
                                node_cop=node_cop.parent
                            return PIECE_VALUE*(change-1)
    return 0

def dist_heuristic(node_state, opponent):
# Heuristic function that adds to the score to decreaes the distance between our coins and opponents coins

    total_dist=0.0
    for our_coin in node_state.data[node_state.to_make_move]:
        for opp_coin in node_state.data[opponent]:
            total_dist+=1.0/((get_dist(our_coin,opp_coin)[X] + get_dist(our_coin,opp_coin)[Y])*node_state.data[node_state.to_make_move][our_coin])
    total_dist /= node_state.no_of_coins[opponent]

    return DISTANCE_VALUE*min(2.3,(total_dist))

def depth_calc(node_state):
# Function that returns the depth minimax AB pruning should go to

    total_coins=node_state.no_of_coins[node_state.playing_as]+node_state.no_of_coins[node_state.opponent]
    log_base=math.floor(5*total_coins*BASE_COEFFICIENT)
    depth=min(MAX_DEPTH_CAP,math.floor(math.log(MAX_NODE_BUDGET,max(MIN_LOG,log_base))))
    
    #If it's odd, perform calculation again, adjusting coin significance
    if depth%2==1:
        total_coins+=0.5*node_state.no_of_coins[node_state.playing_as]
        log_base=math.floor(5*total_coins*BASE_COEFFICIENT)
        depth=min(MAX_DEPTH_CAP,math.floor(math.log(MAX_NODE_BUDGET,max(MIN_LOG,log_base))))

    return depth 

def rep_check(history):
# Examines the last 20 moves to make sure our pieces are not repeating the same thing
# 20 is chosen through a reduction in time (we don't want to spend forever in this function)
# while being large enough to not miss anything important

    # if the history is too small, no useful data can be found
    if len(history)<3:
        return False

    #Initiliase repitive list with the first two moves from either side
    rep_list=history[0:3]
    #Step through history list
    for move in range(3,len(history)):
        # If the previous move is not equal to the most recent move, add it to rep_list
        if history[move] != rep_list[0]:
            rep_list.append(history[move])
        # A pattern will start here. Either it matches or it doesn't.
        else:
            for match_els in range(1,len(history)-move):
                # If it's repeated 3 times, we take it as guaranteed that its repeating
                if match_els>=3:
                    # If we have gotten to this point, there is a pattern for sure
                    return rep_list
                # The pattern does not start here, therefore there is no pattern.
                if rep_list[match_els]!=history[move+match_els]:
                    return False

    # If for some reason we got here, something is wrong. Return False
    return False