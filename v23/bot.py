import random

from battlehack20.stubs import *

# Strategy
# Note that an alternate condition if you can't win by N / 2, is just number of pawns. If you can greedy and decide
# when to push instead of eat, then you can defend and win. Also could be interesting strategy to
# try and sneak some pawns down the side when the middle is locked up.

DEBUG = 0


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
    # dlog('Starting Turn!')
    board_size = get_board_size()

    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    # dlog('Team: ' + str(team))

    robottype = get_type()
    # dlog('Type: ' + str(robottype))

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

        # Trackers to make sure that the capturing is optimized.
        captureLeft = False
        captureRight = False
        prioritizeLeft = False
        prioritizeRight = False

        reinforce = False
        push = True
        opponents = 0
        allies = 0
        # Check to see if you can break favorably
        if check_space_wrapper(row + (forward * 2), col + 1, board_size) == opp_team:
            opponents += 1
            if check_space_wrapper(row + (forward * -1), col + 1, board_size) != team:
                push = False
        if check_space_wrapper(row + (forward * 2), col - 1, board_size) == opp_team:
            opponents += 1
            if check_space_wrapper(row + (forward * -1), col - 1, board_size) != team:
                push = False
        if check_space_wrapper(row, col + 1, board_size) == team:
            allies += 1
        if check_space_wrapper(row, col - 1, board_size) == team:
            allies += 1
        # Make sure the pawns move in the beginning/whenever possible
        if opponents == 2 or allies <= opponents:
            push = False
        if opponents == 0:
            push = True

        # if push:
        # dlog("PUSH")
        # else:
        # dlog("NOPUSH")

        # Make sure you aren't the next in a pawn chain that has to move.
        # TODO: Make sure you're reinforcing the first pawn in a line WHILE not being taken
        # TODO: Make sure if you aren't crucial reinforcement, PUSH PUSH PUSH
        if check_space_wrapper(row + forward, col + 1, board_size) == team and check_space_wrapper(row + (forward * 2),
                                                                                                   col + 2, board_size) == opp_team:  # up and right
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

        # Set the left and right captures to true if possible, aka capture whenever possible, but will be falsified if following conditions apply.
        if check_space_wrapper(row + forward, col + 1, board_size) == opp_team:  # up and right
            captureRight = True
            # dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')

        elif check_space_wrapper(row + forward, col - 1, board_size) == opp_team:  # up and left
            captureLeft = True
            # dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')

        #Check for the arrow pattern, meaning that you should not capture.
        if (check_space_wrapper(row+forward, col, board_size) == opp_team and # Check right in front for an opponent
            check_space_wrapper(row, col+1, board_size) == opp_team and # Check to the right for an opponent
            check_space_wrapper(row, col-1, board_size) == opp_team and # Check to the left for an opponent
            check_space_wrapper(row+(forward*-1), col+1, board_size) == team and # Check one back and to the right for a friendly
            check_space_wrapper(row+(forward*-1), col-1, board_size) == team): # Check one back and to the left for a friendly
            captureLeft = False
            captureRight = False

        # Choose which capture to prioritize, left or right, based on whether pawns are ready to trade on either side.
        rightTrades = 0
        leftTrades = 0
        # Get all the pieces ready to trade to the right
        if check_space_wrapper(row, col+2, board_size) == team: # Check 2 spaces to the right for a friendly.
            rightTrades += 1
            if check_space_wrapper(row+(forward*-1), col+2, board_size) == team: # Check two to the right and one back for a friendly
                rightTrades += 1
                if check_space_wrapper(row+(forward*-2), col+2, board_size) == team: # Check two to the right and two back for a friendly
                    rightTrades += 1
        # Get all the pieces ready to trade to the left
        if check_space_wrapper(row, col-2, board_size) == team: # Check 2 spaces to the left for a friendly.
            leftTrades += 1
            if check_space_wrapper(row+(forward*-1), col-2, board_size) == team: # Check two to the left and one back for a friendly
                leftTrades += 1
                if check_space_wrapper(row+(forward*-2), col-2, board_size) == team: # Check two to the left and two back for a friendly
                    leftTrades += 1

        if rightTrades > leftTrades:
            prioritizeRight = True
        elif leftTrades > rightTrades:
            prioritizeLeft = True
        else:
            prioritizeLeft = prioritizeRight = False
            

        if prioritizeLeft and captureLeft and not prioritizeRight:
            capture(row+forward, col-1) 
        elif prioritizeRight and captureRight and not prioritizeLeft:
            capture(row+forward, col+1)
        elif captureLeft:
            capture(row+forward, col-1) 
        elif captureRight:
            capture(row+forward, col+1)
        # otherwise try to move forward
        elif not (not (row + forward != -1) or not (row + forward != board_size) or check_space_wrapper(row + forward,
                                                                                                        col, board_size)) and not reinforce and push:
            #               ^  not off the board    ^            and    ^ directly forward is empty
            move_forward()
            # dlog('Moved forward!')

    else:
        # Where do we want to spawn the pawns? Center > Edges since you cover two spaces
        # Maybe check to see where the opponent spawned as black and then counter?
        # If you're white, want to go down a lane without any of your pawns not next to one already populated, if populated
        # then you want to just fill a row you already have
        if team == Team.WHITE:
            vert = 0
            # Tracks the base of the opponent
            opp = board_size - 1
            white = True
        else:
            vert = board_size - 1
            opp = 0
            white = False

        # Optimizations:
        # - Don't place if row is won
        # - Don't place if row is gridlocked and rows next are won
        if team == Team.WHITE:
            forward = 1
        else:
            forward = -1

        # First, pick a decent enough col to start off with
        col_to_place = -1
        col_to_place_weight = -1

        # If a lane is uncontested, clog it up
        priority_lane = -1
        # Last resort in case your lane is bad
        last_resort = -1
        for col in range(0, board_size):
            if check_space(opp, col) == team:
                if (col > 0 and check_space(vert + forward, col - 1) != opp_team) and (
                        col < board_size - 1 and check_space(vert + forward, col + 1) != opp_team):
                    last_resort = col
            # Don't spawn if you instantly get eaten
            if check_space_wrapper(vert + forward, col - 1, board_size) == opp_team or check_space_wrapper(
                    vert + forward, col + 1, board_size) == opp_team:
                continue
            col_weight = 0

            for row in range(0, board_size):
                if check_space(row, col) == opp_team:
                    col_weight += abs(row - opp)
                elif check_space(row, col) == team:
                    col_weight -= abs(row - vert)
                # TODO: Your own pawn weight?

            # Checks to make sure there aren't any breakaway pawns
            # Scans from your side to the other!
            priority = False
            for row in range(vert + forward, opp + forward, forward):
                if check_space(row, col) == team:
                    priority = False
                    break
                elif check_space(row, col) == opp_team:
                    priority = True
                    break

            if priority and not check_space(vert, col):
                priority_lane = col
                # dlog("Found priority @ " + str(priority_lane))
                break

            dlog("weight of col is " + str(col_weight))
            # If you're losing harder, then take it
            # Maybe don't take edges.
            if not check_space(vert, col):
                dlog("comparing old: " + str(col_to_place_weight) + " vs new: " + str(col_weight))
                if col_to_place == -1:
                    dlog("default: " + str(col))
                    col_to_place = col
                    col_to_place_weight = col_weight
                elif col_weight > col_to_place_weight:
                    dlog("update: " + str(col))
                    col_to_place = col
                    col_to_place_weight = col_weight

        # If chosen spot is eaten, then you want to go to your last resort which should be behind a won lane
        if check_space_wrapper(vert + forward, col_to_place - 1, board_size) == opp_team or check_space_wrapper(
                vert + forward, col_to_place + 1, board_size) == opp_team:
            if last_resort != -1:
                col_to_place = last_resort

        # dlog("Chosen: " + str(col_to_place))
        # TODO: Change to also evaluate the adjacent columns because they all contrib and spreading out troops is beneficial
        # TODO: cHange to also use same weighting?
        # min_in_row = 0
        # for i in range(0, board_size):
        #     if check_space_wrapper(i, col_to_place, board_size) == team:
        #         min_in_row += 1

        # dlog("row before tests: " + str(col_to_place))
        # for test_col in range(col_to_place - 2, col_to_place + 3):
        #     if 0 > test_col or test_col > board_size - 1:
        #         continue
        #     if check_space(vert, test_col):
        #         continue
        #
        #     in_row = 0
        #     for row in range(0, board_size):
        #         if check_space_wrapper(row, test_col, board_size) == team:
        #             in_row += 1
        #     if in_row < min_in_row:
        #         col_to_place = test_col
        #         min_in_row = in_row

        # dlog("row after tests: " + str(col_to_place))
        # If you find a priority lane with uncontested pawns, challenge it.
        if priority_lane != -1:
            dlog("Chose Priority: " + str(priority_lane))
            spawn(vert, priority_lane)
        elif 0 <= col_to_place <= board_size - 1 and not check_space(vert, col_to_place):
            dlog("Chose: " + str(col_to_place))
            spawn(vert, col_to_place)

        # for _ in range(board_size):
        #    i = random.randint(0, board_size - 1)
        #    if not check_space(index, i):
        #        spawn(vert, i)
        #        dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
        #        break

    bytecode = get_bytecode()
    # dlog('Done! Bytecode left: ' + str(bytecode))
