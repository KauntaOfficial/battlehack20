## This version of the bot primarily focuses on implementing the L function of defense and trading
# It really doesn't do much else yet

import random

from battlehack20.stubs import *


DEBUG = 1
def dlog(str):
    if DEBUG > 0:
        log(str)


global lStage, lCenterLane
# Controls which stage of the L we are currently on
# 0 means nothing has been placed, 1 means the first piece has been placed, 2 means the second piece has been placed
lStage = 0
# lCenterLane controls which lane the L takes place in
lCenterLane = 7


def check_space_wrapper(r, c, board_size):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return False
    try:
        return check_space(r, c)
    except:
        return None

def turn():
    global lStage, lCenterLane
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
        # dlog('My location is: ' + str(row) + ' ' + str(col))

        if team == Team.WHITE:
            forward = 1
        else:
            forward = -1

        # Pawn always wants to capture unless it has can establish control through pushing forward
        # The main strategy here will just be when is not taking a better idea.

        # if not row % 2 and not check_space_wrapper(row + (forward * 2), col + 1, board_size) and not check_space_wrapper(row + (forward * 2), col - 1, board_size) and row + forward != -1 and row + forward != board_size and not check_space_wrapper(row + forward, col, board_size):
        #    move_forward()
        #    dlog('Pushed Forward')
        # try capturing pieces

        reinforce = False
        opponents = 0
        allies = 0
        # Check to see if you can break favorably
        if check_space_wrapper(row + (forward * 2), col + 1, board_size) == opp_team:
            opponents += 1
        if check_space_wrapper(row + (forward * 2), col - 1, board_size) == opp_team:
            opponents += 1
        if check_space_wrapper(row, col + 1, board_size) == team:
            allies += 1
        if check_space_wrapper(row, col - 1, board_size) == team:
            allies += 1
        # Make sure the pawns move in the beginning/whenever possible
        if opponents == 0:
            allies += 1

        # Make sure you aren't the next in a pawn chain that has to move.
        # TODO: Make sure you're reinforcing the first pawn in a line WHILE not being taken
        # TODO: Make sure if you aren't crucial reinforcement, PUSH PUSH PUSH
        if check_space_wrapper(row + forward, col + 1, board_size) == team and check_space_wrapper(row + (forward * 2),
                                                                                                   col + 2,
                                                                                                   board_size) == opp_team:  # up and right
            reinforce = True
        elif check_space_wrapper(row + forward, col - 1, board_size) == team and check_space_wrapper(
                row + (forward * 2), col - 2, board_size) == opp_team:  # up and left
            reinforce = True
        elif check_space_wrapper(row + forward, col + 1, board_size) == team and check_space_wrapper(
                row + (forward * 2), col, board_size) == opp_team:
            reinforce = True
        elif check_space_wrapper(row + forward, col - 1, board_size) == team and check_space_wrapper(
                row + (forward * 2), col, board_size) == opp_team:
            reinforce = True

        # if check_space_wrapper(row + (forward * 2), col + 1, board_size) == team and opponents == 0:
        #     reinforce = False
        # if check_space_wrapper(row + (forward * 2), col - 1, board_size) == team and opponents == 0:
        #     reinforce = False
        # Make sure you push to the end if possible
        if row + forward == 0 or row + forward == board_size - 1:
            reinforce = False

        if check_space_wrapper(row + forward, col + 1, board_size) == opp_team:  # up and right
            capture(row + forward, col + 1)
            # dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')

        elif check_space_wrapper(row + forward, col - 1, board_size) == opp_team:  # up and left
            capture(row + forward, col - 1)
            # dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')

        # otherwise try to move forward
        elif not (not (row + forward != -1) or not (row + forward != board_size) or check_space_wrapper(row + forward,
                                                                                                        col,
                                                                                                        board_size)) and allies > opponents and not reinforce:
            #               ^  not off the board    ^            and    ^ directly forward is empty
            move_forward()
            # dlog('Moved forward!')

    else:
        # Step variable is used so that code translates to both teams.
        if team == Team.WHITE:
            vert = 0
            opp = board_size - 1
            step = 1
        else:
            vert = board_size - 1
            opp = 0
            step = -1

        if lStage == 0:
            lStage = 1
            lCenterLane = spawnLanev4(vert, opp, step, team, opp_team, board_size)
            spawn(vert, lCenterLane)
            
        # Occurs when the first piece of the L is placed, places the second piece.
        elif lStage == 1:
            if lCenterLane > 7:
                offset = -1
            else:
                offset = 1

            # Check to see if either of the sides are available, otherwise just decide on which space to go to based on the original placement algorithm, starting the process over.
            if not check_space_wrapper(vert, lCenterLane + offset, board_size):
                spawnLocation = lCenterLane + offset
                spawn(vert, spawnLocation)
                lStage = 2
            # if first choice location is not available, try the other side
            elif not check_space_wrapper(vert, lCenterLane - offset, board_size):
                spawnLocation = lCenterLane - offset
                lStage = 2
                spawn(vert, spawnLocation)
            # If neither location is available, go back to the start of the L formation.
            else:
                lStage = 1
                lCenterLane = spawnLanev1(vert, opp, step, team, opp_team, board_size)
                spawn(vert, lCenterLane)
            
            

        # Occurs during the final stage of the L, places the final piece.
        elif lStage == 2:
            lStage = 0
            if not check_space_wrapper(vert, lCenterLane, board_size):
                spawn(vert, lCenterLane)
            # if you cannot place the final piece, go back to starting another L
            else:
                lstage = 1
                lCenterLane = spawnLanev4(vert, opp, step, team, opp_team, board_size)
                spawn(vert, lCenterLane)


def spawnLanev1(vert, opp, step, team, opp_team, board_size):
    # Optimizations:
    # - Don't place if row is won
    # - Don't place if row is gridlocked and rows next are won
    if team == Team.WHITE:
        forward = 1
    else:
        forward = -1

    col_to_place = -1
    for col in range(0, board_size):
        if not check_space(vert, col):
            if check_space_wrapper(vert + forward, col - 1, board_size) == opp_team or check_space_wrapper(vert + forward, col + 1, board_size) == opp_team:
                continue

            col_to_place = col
            break

    if col_to_place == -1:
        for col in range(0, 15):
            if not check_space(vert, col):
                col_to_place = col
                break

    diff = 0
    for row in range(0, board_size):
        if check_space(row, col_to_place) == opp_team:
            diff -= 1
        elif check_space(row, col_to_place) == team:
            diff += 1

    last_resort = -1
    for col in range(0, board_size):
        if check_space(opp, col) == team:
            if (col > 0 and check_space(vert + forward, col - 1) != opp_team) and (col < 15 and check_space(vert + forward, col + 1) != opp_team):
                last_resort = col
        if col > 0 and check_space(vert + forward, col - 1) == opp_team:
            continue
        if col < 15 and check_space(vert + forward, col + 1) == opp_team:
            continue
        opp_count = 0
        your_count = 0

        for row in range(0, board_size):
            if check_space(row, col) == opp_team:
                opp_count += 1
            elif check_space(row, col) == team:
                your_count += 1

        # if 0 < col < 15:
        #     if check_space(opp, col - 1) == team and check_space(opp, col + 1) == team:
        #         if your_count == 0:
        #             col_to_place = col
        #             break
        #         else:
        #             continue

        if your_count - opp_count <= diff and not check_space(vert, col):
            col_to_place = col
            diff = your_count - opp_count

    if check_space_wrapper(vert + forward, col_to_place - 1, board_size) == opp_team or check_space_wrapper(vert + forward, col_to_place + 1, board_size) == opp_team:
        if last_resort != -1:
            col_to_place = last_resort

    # dlog("Chosen: " + str(col_to_place))
    if 0 <= col_to_place <= 15 and not check_space(vert, col_to_place):
        return col_to_place
        

    # for _ in range(board_size):
    #    i = random.randint(0, board_size - 1)
    #    if not check_space(index, i):
    #        spawn(vert, i)
    #        dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
    #        break

## Spawning version coming in from v4 of Ivy's system
def spawnLanev4(vert, opp, step, team, opp_team, board_size):
    # Optimizations:
    # - Don't place if row is won
    # - Don't place if row is gridlocked and rows next are won
    if team == Team.WHITE:
        forward = 1
    else:
        forward = -1


    # First, pick a decent enough col to start off with
    col_to_place = -1
    for col in range(0, board_size):
        if not check_space(vert, col):
            if check_space_wrapper(vert + forward, col - 1, board_size) == opp_team or check_space_wrapper(
                    vert + forward, col + 1, board_size) == opp_team:
                continue

            col_to_place = col
            break

    if col_to_place == -1:
        for col in range(0, 15):
            if not check_space(vert, col):
                col_to_place = col
                break

    # Find the column where you are losing hardest (their pawn count - yours)
    diff = 0
    for row in range(0, board_size):
        if check_space(row, col_to_place) == opp_team:
            diff -= 1
        elif check_space(row, col_to_place) == team:
            diff += 1

    # If a lane is uncontested, clog it up
    priority_lane = -1
    # Last resort in case your lane is bad
    last_resort = -1
    for col in range(0, board_size):
        if check_space(opp, col) == team:
            if (col > 0 and check_space(vert + forward, col - 1) != opp_team) and (
                    col < 15 and check_space(vert + forward, col + 1) != opp_team):
                last_resort = col
        # Don't spawn if you instantly get eaten
        if col > 0 and check_space(vert + forward, col - 1) == opp_team:
            continue
        if col < 15 and check_space(vert + forward, col + 1) == opp_team:
            continue
        opp_count = 0
        your_count = 0

        for row in range(0, board_size):
            if check_space(row, col) == opp_team:
                opp_count += 1
            elif check_space(row, col) == team:
                your_count += 1

        # Checks to make sure there aren't any breakaway pawns
        # Scans from your side to the other!
        priority = True
        for row in range(vert + forward, opp, forward):
            if check_space(row, col) == team:
                priority = False
            elif check_space(row, col) == opp_team:
                break

        if priority and not check_space(vert, col):
            priority_lane = col
            break

        # If you're losing harder, then take it
        if your_count - opp_count <= diff and not check_space(vert, col):
            col_to_place = col
            diff = your_count - opp_count

    # If chosen spot is eaten, then you want to go to your last resort which should be behind a won lane
    if check_space_wrapper(vert + forward, col_to_place - 1, board_size) == opp_team or check_space_wrapper(
            vert + forward, col_to_place + 1, board_size) == opp_team:
        if last_resort != -1:
            col_to_place = last_resort

    # dlog("Chosen: " + str(col_to_place))
    # TODO: Change to also evaluate the adjacent columns because they all contrib and spreading out troops is beneficial
    min_in_row = 0
    for i in range(0, board_size):
        if check_space_wrapper(i, col_to_place, board_size) == team:
            min_in_row += 1

    for test_col in range(col_to_place - 1, col_to_place + 2):
        if 0 > test_col or test_col > 15:
            continue
        if check_space(vert, test_col):
            continue

        in_row = 0
        for row in range(0, board_size):
            if check_space_wrapper(row, test_col, board_size) == team:
                in_row += 1
        if in_row < min_in_row:
            col_to_place = test_col
            min_in_row = in_row

    # If you find a priority lane with uncontested pawns, challenge it.
    if priority_lane != -1:
        return priority_lane
    elif 0 <= col_to_place <= 15 and not check_space(vert, col_to_place):
        return col_to_place

    # for _ in range(board_size):
    #    i = random.randint(0, board_size - 1)
    #    if not check_space(index, i):
    #        spawn(vert, i)
    #        dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
    #        break
    
    
    
            


    bytecode = get_bytecode()
    dlog('Done! Bytecode left: ' + str(bytecode))

