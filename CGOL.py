import tkinter as tk
from Rules import RULES
from time import sleep


# unmap(WINDOW, {
#     'geometry' : f"{W}x{H}",
#     'wm_title' : "CGOL",
#     "wm_resizable" : (False,False),
# })



def grid(W, H, D):
    """
    Generates a grid.
    :param W: width
    :param H: height
    :param D: default value
    :return:
    """
    out = []
    for k in range(H):
        out += [[D] * W]
    return out


class OnTheFly:
    def __init__(self, **data):
        for key,val in data.items():
            exec(f"self.{key} = {val}")


# def unmap(obj, functions:{}):
#     for func,args in functions.items():
#         exec(f"{obj}.{func}( {type(args)}({args}) )")



#smolBord = OnTheFly(w=8)

def clamp(value:int or float, minimum:int or float, maximum:int or float) -> (int or float):
    """
    Bounds a value within an interval.
    The value is unchanged if it was already in between, otherwise the nearest boundary is returned.

    :param value: Value to be clamped.
    :param minimum: Lowest value.
    :param maximum: Highest value.
    :return: 'value' within the ['minimum' ; 'maximum'] interval.
    """
    return min(
        max(value,minimum),
        maximum,
    )

def strip(array:[], value):
    """
    Strips all occurences of value within array.

    :param array: A list containing 'value' any number of times >= 0.
    :param value: Any object to be excluded from 'array'.
    :return: 'value'-less 'array'.
    """
    return [element for element in array if element != value]

def cut(table:[[bool]], pos:[int,int], radius:int=1):
    """
    This may be rewritten eventually as I believe it could be made more compact.
    Perhaps even into a one-liner ?

    :param table: Duo-dimensional grid of booleans to be cut.
    :param pos: Couple of coordinates to center onto.
    :param radius: Amount of tiles to look for from the given 'pos' (including diagonals). This is the radius of a square.
    """
    out = []
    for line in table[max(pos[1]-radius,0) : min(pos[1]+radius,len(table))+1]:
        out += [line[max(pos[0]-radius,0) : min(pos[0]+radius,len(table[0]))+1]]
    return out

def countNeighbours(table:[[bool]], state:bool):
    """
    Adds all rows of 'table' together, then adds their integer form,
    which is equal to the amount of live cells in the given region ('table'),
    which we then subtract the 'state' of the middle state from as not to count it.

    :param table: Duo-dimensional list where each cell is a boolean value.
    :param state: Current (~middle) cell state.
    :return: Amount of neighbours of the cell, of which the state is given.
    """
    return sum( [int(cell) for cell in sum(table, [])] ) - int(state)


def relativeCoordinates(pos:[int,int], dim:[int,int]):
    """
    Invoked in order to define a starting position and a dimension,
    the latter being relative to the former,
    instead of declaring two absolute positions.

    :param pos: Position
    :param dim: Dimensions (size)
    :return: tkinter compatible set of coordinates (`x1,y1,x2,y2`)
    """
    return (
        pos[0],
        pos[1],
        pos[0]+dim[0],
        pos[1]+dim[1],
    )


def drawGrid(table:[[bool]], canvas:tk.Canvas, cam_pos:[int,int]):
    """
    Draw each cell of 'table' onto the given 'canvas'.
    The dimensions and other caracteristics of the cells are defined as local variables within the function,
    which may be moved into **keyword_arguments.
    """

    canvas.delete(tk.ALL) # canvases actually keep track of all their objects, even when fully drawn over,
                          # so this line is extremely important as to avoid any slow downs
    ### [NOTE] : show the others what used to happen before i found that out
    ###          (as I don't recall its necessity being documented anywhere officially...)

    cell_size:int = 8
    border_width:int = 1
    outline_width:int = int(CANVAS.cget('highlightthickness'))

    for y in range(len(table)):
        for x in range(len(table[0])):
            canvas.create_rectangle(
                relativeCoordinates(
                    [x*cell_size + border_width*x + outline_width - cam_pos[0],
                     y*cell_size + border_width*y + outline_width - cam_pos[1]],
                    [cell_size]*2,
                ),
                fill=["black","white"][table[y][x]],
                outline="",
            )


def liftWindow(win):
    """
    Small utility to ensure the given window ('win') appears immediately and receives focus automatically.
    (since for some reason this is not default behaviour)

    :param win: Tk() object.
    """
    win.lift()
    win.attributes('-topmost', True)
    win.attributes('-topmost', False)
    win.focus_force()





def init():
    """
    Called once, before tick().
    Setups everything.
    """

    global WH, W, H
    WH = W, H = 255, 255

    board_width = input("Board width [cells] : ")  or W//8
    board_height = input("Board height [cells] : ") or H//8

    global BOARD, IS_RUNNING
    BOARD = grid(
        int(board_width),
        int(board_height),
        False
    )
    IS_RUNNING = True

    global WINDOW
    WINDOW = tk.Tk()
    WINDOW.geometry(f"{W}x{H}")
    WINDOW.wm_title("CGOL")
    WINDOW.wm_resizable(False, False)
    WINDOW.bind('<KeyRelease-space>', lambda event: (
        globals().update(IS_RUNNING=not IS_RUNNING),
        # print("Running" if IS_RUNNING else "Suspended"),
    ))
    WINDOW.bind('<Left>', lambda event: (
        globals().update(CAM_POS=[CAM_POS[0] - 1, CAM_POS[1]])
    ))
    WINDOW.bind('<Right>', lambda event: (
        globals().update(CAM_POS=[CAM_POS[0] + 1, CAM_POS[1]])
    ))
    WINDOW.bind('<Up>', lambda event: (
        globals().update(CAM_POS=[CAM_POS[0], CAM_POS[1] - 1])
    ))
    WINDOW.bind('<Down>', lambda event: (
        globals().update(CAM_POS=[CAM_POS[0], CAM_POS[1] + 1])
    ))
    liftWindow(WINDOW)  # jump above all other windows (pin >> unpin)


    global CANVAS
    CANVAS = tk.Canvas(width=256, height=256, bg="#202020", highlightbackground="#202020")  # highlightthickness=0
    CANVAS.pack()

    global CAM_POS
    # CAM = OnTheFly(x=0, y=0)
    CAM_POS = [0]*2

    # BOARD[4][4] = True
    # BOARD[4][5] = True
    # BOARD[4][6] = True

    cells_temp = [
        (0,2),
        (1,0),(1,2),
        (2,1),(2,2),
    ]
    for cell in cells_temp:
        BOARD[cell[0]][cell[1]] = True


def tick():
    """
    Called repeatedly, after init().
    Execute all actions each frame, including drawing the grid,
    refreshing the window, and computing the next iteration of the board.
    """

    global BOARD

    while True:
        # # temporary way of printing to the terminal
        # [print(
        #     # "  ".join([str(int(item)) for item in line])
        #     " ".join(
        #         [('⬜','⬛')[item] for item in line]
        #     )
        # ) for line in BOARD]
        # print()

        drawGrid(BOARD, CANVAS, CAM_POS)
        WINDOW.update()

        if not IS_RUNNING: continue


        # BOARD at frame+1,
        # as modifying the current BOARD would have undesirable consequences on the latter cells
        # pregen next frame
        next_board = grid(
            len(BOARD[0]),
            len(BOARD),
            False,
        )

        # run every rule for each cell
        # no need for `enumerate` as we are only interested in the index,
        # and the value at **both** coordinates
        # (could probably use a single for loop but the number of iterations would stay the same)
        for y in range(len(BOARD)):
            for x in range(len(BOARD[y])):
                cellState:bool = BOARD[y][x]
                neighbours:int = countNeighbours(
                    cut(BOARD,[x,y],1),
                    cellState,
                )

                # remove None from the list of the values returned by each rule,
                # only leaving those which would change the state of the current cell
                next_cell = strip(
                    [rule(c=cellState, n=neighbours) for rule in RULES],
                    None,
                )

                # set the value of this cell at the next frame to be the last value of the aforementioned list,
                # as precedence is determined this way (corresponds to the order of the functions in RULES).
                next_board[y][x] = (
                    next_cell[-1]
                    if len(next_cell) != 0
                    else BOARD[y][x]
                )

        BOARD = next_board # and finally apply all modifications
                           # (this is not returned, as this is the `tick()` function).
                           # (had it been its own function, then it probably would've been returned)
        # sleep(0.25)



if __name__ == '__main__':
    init()
    tick()

