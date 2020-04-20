import random

from battlehack20.stubs import *

# Strategy
# Note that an alternate condition if you can't win by N / 2, is just number of pawns. If you can greedy and decide
# when to push instead of eat, then you can defend and win. Also could be interesting strategy to
# try and sneak some pawns down the side when the middle is locked up.

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
    # dlog('Starting Turn!')
    board_size = get_board_size()

    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    # dlog('Team: ' + str(team))

    robottype = get_type()
    # dlog('Type: ' + str(robottype))

    if team == Team.WHITE:
        vert = 0
        # Tracks the base of the opponent
        opp = board_size - 1
        white = True
    else:
        vert = board_size - 1
        opp = 0
        white = False

    if robottype == RobotType.PAWN:
        row, lane = get_location()
        # dlog('My location is: ' + str(row) + ' ' + str(col))

        if team == Team.WHITE:
            forward = 1
        else:
            forward = -1

        # This part here is a custom version of sense, which means that I can create my own formats.
        # Specific order for my own good.
        surroundings = []
        opponents = 0
        allies = 0
        open = 0

        # In front of the pawn will *always* be the higher numbers, so don't need to use forward when 
        # using this list in the future.
        for r in range(row - (2*forward), row + (2*forward)):
            thisRow = []
            for l in range(lane - 2, lane + 2):
                if r >= 0 and r <= 15 and l >= 0 and l <= 15:
                    space=check_space_wrapper(r, l, board_size)
                    dlog(str(space))
                    thisRow.append(space)
                    # Increase the opponent and ally counters
                    if space == team:
                        allies += 1
                    elif space == opp_team:
                        opponents += 1
                    elif not space:
                        open += 1
                else:
                    # This designates that that spot is out of bounds.
                    thisRow.append("OOB")
            surroundings.append(thisRow)

        dlog(str(surroundings))

        move=True
        captureRight=False
        captureLeft=False
        stayPut = False

        alliesToTheSides=0
        for space in list(surroundings[2][1], surroundings[2][3]):
            if space == team:
                alliesToTheSides += 1

        # Check for opponenets that are a knight's move away.
        oppsKnightAway=0
        for space in list(surroundings[4][1], surroundings[4][3]):
            if space == opp_team:
                oppsKnightAway += 1

        # Make sure the pawns move whenever possible.
        if oppsKnightAway == 0:
            alliesToTheSides += 1

        # Set the row and the lane based on where the player is in the surroundings array.
        r=2
        l=2

        # Move to the end if the next space is the end of the board.
        if row + forward == opp:
            move=True

        # Checks to see if the current pawn is a pawn that should stay put to help another pawn.
        for checkLane in list(l - 1, l + 1):
            for furtherLane in list(checkLane-1, checkLane+1):
                if surroundings[r+1][checkLane] == team and surroundings[r+2][furtherLane] == opp_team:
                    stayPut = True

        # Set the flags for capturing if possible.        
        if surroundings[r+1][l+1] == opp_team:
            captureRight = True
        elif surroundings[r+1][l+1] == opp_team:
            captureLeft = True
        # TODO Double check the validity of the allies > opponents part. Currently, allies > opponents is deleted.
        elif (row != opp) and surroundings[r+1][l]!=False and not stayPut:
            move=True

        
        #Execute the instructions
        if stayPut:
            pass
        elif captureLeft:
            capture(row+forward, lane-1)
        elif captureRight:
            capture(row+forward, lane+1)  
        elif move:
            move_forward()

    else:
        # Where do we want to spawn the pawns? Center > Edges since you cover two spaces
        # Maybe check to see where the opponent spawned as black and then counter?
        # If you're white, want to go down a lane without any of your pawns not next to one already populated, if populated
        # then you want to just fill a row you already have


        # Optimizations:
        # - Don't place if row is won
        # - Don't place if row is gridlocked and rows next are won
        if team == Team.WHITE:
            forward=1
        else:
            forward=-1

        # First, pick a decent enough col to start off with
        col_to_place=-1
        for col in range(0, board_size):
            if not check_space(vert, col):
                if check_space_wrapper(vert + forward, col - 1, board_size) == opp_team or check_space_wrapper(
                        vert + forward, col + 1, board_size) == opp_team:
                    continue

                col_to_place=col
                break

        if col_to_place == -1:
            for col in range(0, board_size):
                if not check_space(vert, col):
                    col_to_place=col
                    break

        # Find the column where you are losing hardest (their pawn count - yours)
        diff=0
        for row in range(0, board_size):
            if check_space(row, col_to_place) == opp_team:
                diff -= 1
            elif check_space(row, col_to_place) == team:
                diff += 1

        # If a lane is uncontested, clog it up
        priority_lane=-1
        # Last resort in case your lane is bad
        last_resort=-1
        for col in range(0, board_size):
            if check_space(opp, col) == team:
                if (col > 0 and check_space(vert + forward, col - 1) != opp_team) and (
                        col < board_size - 1 and check_space(vert + forward, col + 1) != opp_team):
                    last_resort=col
            # Don't spawn if you instantly get eaten
            if check_space_wrapper(vert + forward, col - 1, board_size) == opp_team or check_space_wrapper(
                    vert + forward, col + 1, board_size) == opp_team:
                continue
            opp_count=0
            your_count=0

            for row in range(0, board_size):
                if check_space(row, col) == opp_team:
                    opp_count += 1
                elif check_space(row, col) == team:
                    your_count += 1

            # Checks to make sure there aren't any breakaway pawns
            # Scans from your side to the other!
            priority=False
            for row in range(vert + forward, opp + forward, forward):
                if check_space(row, col) == team:
                    priority=False
                    break
                elif check_space(row, col) == opp_team:
                    priority=True
                    break

            if priority and not check_space(vert, col):
                priority_lane=col
                # dlog("Found priority @ " + str(priority_lane))
                break

            # If you're losing harder, then take it
            # Maybe don't take edges.
            if your_count - opp_count <= diff and not check_space(vert, col):
                col_to_place=col
                diff=your_count - opp_count

        # If chosen spot is eaten, then you want to go to your last resort which should be behind a won lane
        if check_space_wrapper(vert + forward, col_to_place - 1, board_size) == opp_team or check_space_wrapper(
                vert + forward, col_to_place + 1, board_size) == opp_team:
            if last_resort != -1:
                col_to_place=last_resort

        # dlog("Chosen: " + str(col_to_place))
        # TODO: Change to also evaluate the adjacent columns because they all contrib and spreading out troops is beneficial
        min_in_row=0
        for i in range(0, board_size):
            if check_space_wrapper(i, col_to_place, board_size) == team:
                min_in_row += 1

        dlog("row before tests: " + str(col_to_place))
        for test_col in range(col_to_place - 2, col_to_place + 3):
            if 0 > test_col or test_col > board_size - 1:
                continue
            if check_space(vert, test_col):
                continue

            in_row=0
            for row in range(0, board_size):
                if check_space_wrapper(row, test_col, board_size) == team:
                    in_row += 1
            if in_row < min_in_row:
                col_to_place=test_col
                min_in_row=in_row

        dlog("row after tests: " + str(col_to_place))
        # If you find a priority lane with uncontested pawns, challenge it.
        if priority_lane != -1:
            # dlog("Chose Priority: " + str(priority_lane))
            spawn(vert, priority_lane)
        elif 0 <= col_to_place <= board_size - 1 and not check_space(vert, col_to_place):
            # dlog("Chose: " + str(col_to_place))
            spawn(vert, col_to_place)

        # for _ in range(board_size):
        #    i = random.randint(0, board_size - 1)
        #    if not check_space(index, i):
        #        spawn(vert, i)
        #        dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
        #        break

    bytecode=get_bytecode()
    # dlog('Done! Bytecode left: ' + str(bytecode))
