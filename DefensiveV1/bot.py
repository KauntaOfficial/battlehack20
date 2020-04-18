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
        if check_space_wrapper(row + forward, col + 1, board_size) == opp_team:  # up and right
            capture(row + forward, col + 1)
            # dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')

        elif check_space_wrapper(row + forward, col - 1, board_size) == opp_team:  # up and left
            capture(row + forward, col - 1)
            # dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')

        # otherwise try to move forward
        elif row + forward != -1 and row + forward != board_size and not check_space_wrapper(row + forward, col,
                                                                                             board_size):
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

        col_to_place = -1
        for col in range(0, 15):
            if not check_space(vert, col) and not check_space(opp, col) == team:
                if col > 0 and check_space(vert + forward, col - 1) == opp_team:
                    continue
                if col < 15 and check_space(vert + forward, col + 1) == opp_team:
                    continue

                col_to_place = col
                break

        if col_to_place == -1:
            for col in range(0, 15):
                if not check_space(vert, col):
                    col_to_place = col
                    break

        diff = 0
        for row in range(0, 15):
            if check_space(row, col_to_place) == opp_team:
                diff -= 1
            elif check_space(row, col_to_place) == team:
                diff += 1

        for col in range(0, 15):
            if check_space(opp, col) == team:
                continue

            opp_count = 0
            your_count = 0

            for row in range(0, 15):
                if check_space(row, col) == opp_team:
                    opp_count += 1
                elif check_space(row, col) == team:
                    your_count += 1

            if 0 < col < 15:
                if check_space(opp, col - 1) == team and check_space(opp, col + 1) == team:
                    if your_count == 0:
                        col_to_place = col
                        break
                    else:
                        continue

            if your_count - opp_count < diff and not check_space(vert, col):
                col_to_place = col
                diff = your_count - opp_count

        spawn(vert, col_to_place)

        # for _ in range(board_size):
        #    i = random.randint(0, board_size - 1)
        #    if not check_space(index, i):
        #        spawn(vert, i)
        #        dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
        #        break

    bytecode = get_bytecode()
    # dlog('Done! Bytecode left: ' + str(bytecode))
