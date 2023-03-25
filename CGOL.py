import tkinter as tk
from Rules import RULES
from time import sleep




### globals (will be moved to init later on)

IS_RUNNING = True


WH = W,H = 255,255

WINDOW = tk.Tk()
# unmap(WINDOW, {
#     'geometry' : f"{W}x{H}",
#     'wm_title' : "CGOL",
#     "wm_resizable" : (False,False),
# })
WINDOW.geometry(f"{W}x{H}")
WINDOW.wm_title("CGOL")
WINDOW.wm_resizable(False,False)
WINDOW.bind('<KeyRelease-space>', lambda event: (globals().update(IS_RUNNING=not IS_RUNNING), print(IS_RUNNING), None))

CANVAS = tk.Canvas(width=256,height=256, bg="#202020", highlightbackground="#202020") # highlightthickness=0
CANVAS.pack()

###



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

def clamp(value, minimum, maximum):
    """my head is hurting, but trust me it made sense when i wrote it"""
    return min(
        max(value,minimum),
        maximum,
    )

def strip(array:[], value):
    return [element for element in array if element != value]

def cut(table:[[bool]], pos:[int,int], radius:int=1):
    """
    This may be rewritten eventually as I believe it could be made more compact.
    Perhaps even into a one-liner ?
    """
    out = []
    #pos[0] = min(max(radius, pos[0]), len(table))
    #pos[1] = min(max(radius, pos[1]), len(table[0]))

    for line in table[max(pos[1]-radius,0) : min(pos[1]+radius,len(table))+1]:
        out += [line[max(pos[0]-radius,0) : min(pos[0]+radius,len(table[0]))+1]]
    return out

def countNeighbours(table:[[bool]], state:bool):
    """

    :param table: Duo-dimensional list
    :param state: Current (~middle) cell state
    :return: Amount of neighbours of the cell of which the state is given
    """
    return sum( [int(cell) for cell in sum(table, [])] ) - int(state)


def relativeCoordinates(pos:[int,int], dim:[int,int]):
    """
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


def drawGrid(table:[[bool]], canvas:tk.Canvas):
    canvas.delete(tk.ALL) # canvases actually keep track of all their objects,
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
                    [x*cell_size + border_width*x + outline_width,
                     y*cell_size + border_width*y + outline_width],
                    [cell_size]*2,
                ),
                fill=["black","white"][table[y][x]],
                outline="",
            )





def init():
    global BOARD

    board_width = input("Board width [cells] : ")  or int(CANVAS.cget('width')) // 8
    board_height = input("Board height [cells] : ") or int(CANVAS.cget('width')) // 8

    WINDOW.lift() # jump above all other windows (not pinned)

    BOARD = grid(int(board_width), int(board_height), False)

    # BOARD[4][4] = True
    # BOARD[4][5] = True
    # BOARD[4][6] = True

    # cells_temp = [
    #     (0,2),
    #     (1,0),(1,2),
    #     (2,1),(2,2),
    # ]
    # for cell in cells_temp:
    #     BOARD[cell[0]][cell[1]] = True


def tick():
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


        drawGrid(BOARD, CANVAS)
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
        for y in range(len(BOARD)):
            for x in range(len(BOARD[y])):
                cellState:bool = BOARD[y][x]
                neighbours:int = countNeighbours(
                    cut(BOARD,[x,y],1),
                    cellState,
                )

                next_cell = strip(
                    [rule(c=cellState, n=neighbours) for rule in RULES],
                    None,
                )

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

