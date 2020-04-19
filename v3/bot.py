## This version of the bot primarily focuses on implementing the L function of defense and trading
# It really doesn't do much else yet

import random

from battlehack20.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

DEBUG = 1
def dlog(str):
    if DEBUG > 0:
        log(str)


def check_space_wrapper(r, c, board_size):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return False
    try:
        return check_space(r, c)
    except:
        return None

def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """
    dlog('Starting Turn!')
    board_size = get_board_size()

    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    dlog('Team: ' + str(team))

    robottype = get_type()
    dlog('Type: ' + str(robottype))

    if robottype == RobotType.PAWN:
        row, col = get_location()
        dlog('My location is: ' + str(row) + ' ' + str(col))

        if team == Team.WHITE:
            forward = 1
        else:
            forward = -1

        # try catpuring pieces
        if check_space_wrapper(row + forward, col + 1, board_size) == opp_team: # up and right
            capture(row + forward, col + 1)
            dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')

        elif check_space_wrapper(row + forward, col - 1, board_size) == opp_team: # up and left
            capture(row + forward, col - 1)
            dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')

        # otherwise try to move forward
        elif row + forward != -1 and row + forward != board_size and not check_space_wrapper(row + forward, col, board_size):
            #               ^  not off the board    ^            and    ^ directly forward is empty
            move_forward()
            dlog('Moved forward!')

    else:
        # Step variable is used so that code translates to both teams.
        if team == Team.WHITE:
            index = 0
            oppIndex = board_size - 1
            step = 1
        else:
            index = board_size - 1
            oppIndex = 0
            step = -1

        board = get_board()
        # Create an array of priority lanes, the lower the index, the higher the priority.
        # So far, this is only based on how close the opponents pieces are to your side.
        # TODO Fix the problem here with the rows and cols
        priorityLanes = []
        for row in range(index + step, oppIndex, step):
            oppInRow = False
            for lane in range(0,15):
                if board[row][lane] == opp_team and (lane not in priorityLanes):
                    priorityLanes.append(lane)

        for _ in priorityLanes:
            dlog(str(_))

        ## sets the center as the prioritized lane if the opponent has no units down.
        if len(priorityLanes) == 0:
            priorityLanes.append(7)
        
        
        # Figure out which lanes already have L formations in them. 
        spawnLane = -1
        for lane in priorityLanes:
            teamPawnsInLane = 0
            for i in range(oppIndex, index + (2 * step), step):
                if board[i][lane] == team:
                    teamPawnsInLane += 1
            
            ## If there is only one pawn in the current highest priority lane, then form the L behind them
            # Also be sure to check if the side part of the L has already been placed.
            # TODO optimize which side the L is placed on
            if teamPawnsInLane == 1:
                if check_space(index + step, lane-1) == team or check_space(index + step, lane+1) == team:
                    # If either of these are true, all that's left to do is place the final piece beneath the original piece.
                    spawnLane = lane
                else:
                    spawnLane = lane + (1 if (random.randint(0,1) == 1 or (lane == 0)) and not lane == 15 else -1) #what the fuck python why does this work
            elif teamPawnsInLane <=2:
                break
            else:
                spawnLane = lane
        if spawnLane < 0:
            spawnLane = priorityLanes.pop()

        while True:
            try:
                spawn(index, spawnLane)
                break
            except:
                try:
                    spawnLane = priorityLanes.pop()
                except:
                    spawnLane = (spawnLane + 1) % 15
            


    bytecode = get_bytecode()
    dlog('Done! Bytecode left: ' + str(bytecode))

