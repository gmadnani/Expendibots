# Expendibots

## Setup
Expendibots is played on a 88 board consisting of 64 squares, as illustrated in Figure 1. Two players, White
and Black, play the game. Each player initially controls 12 tokens of their own colour. The pieces begin in
the conguration shown below in Figure 1, occupying the back two rows in 3 square formations. One or more
tokens of the same colour on a single square form a stack; for ease of rendering in 2D, we depict the number of
tokens in a stack by a number placed on the token in the diagram. In the initial position, all stacks are of size 1
(a single token).

## Gameplay
Players alternate taking turns, with White having the rst turn. This cycle repeats until the game ends. On
each turn, the current player must take a single action involving a stack of their colour. This action may be a
move action or a boom action. Each type of action is described in the following sections.

## Move actions
A move action (a `move') involves moving some or all of the tokens in a stack some number of squares in one
of the four cardinal directions | up, down, left, or right. From a stack of n tokens (n  1), the player may move
up to n of those tokens a distance of up to n squares in a single direction. The tokens may not move diagonally,
and must move by at least one square. The destination square may be unoccupied, or it may already be occupied
by tokens of the same colour | in this case, the moved tokens join the tokens on the destination square, forming
a new stack whose number of tokens is equal to the number of tokens originally on the square plus the number
of tokens moved onto the square. The tokens may not move onto a square occupied by the opponent's tokens.
However, the tokens may move `over' it (as long as the total distance moved is not more than n squares). A
token cannot move o the board. There is no limit to the number of tokens in a stack.

## Boom actions
A boom action (a `boom') involves choosing a stack to explode. All of the tokens in this stack are removed from
play as a result of this explosion. Additionally, the explosion immediately causes any stacks (of either color) in
a 3  3 area surrounding this stack to also explode. These explosions may go on to trigger further explosions in
a recursive chain reaction. In this way, long chains of stacks may be removed from play as the result of a single
action.

## Ending the game
The game ends as soon as at least one player has no remaining tokens. At this point, the player who still has at
least one token is declared the winner. If both players lose their remaining tokens simultaneously, the game is
declared a draw. A draw is also declared if either of the following conditions are met:
 One board conguration (with all stacks in the same position and quantity) occurs for a fourth time since
the start of the game. These repeated board congurations do not need to occur in succession.
 Each player has had their 250th turn without a winner being declared.