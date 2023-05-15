import tkinter as tk
from Rules import RULES
from time import sleep
import ConsoleUtil as con


# unmap(WINDOW, {
#     'geometry' : f"{W}x{H}",
#     'wm_title' : "CGOL",
#     "wm_resizable" : (False,False),
# })


class Board(list):
    cell_dim:[int,int] = [8]*2
    gap:[int,int] = [0]*2
    def __init__(self, seq=(), **kwargs):
        super().__init__(seq)
        for key,val in kwargs.items():
            exec(f"self.{key} = {val}")
        # self.cell_dim = kwargs.get('cell_dim', Board.cell_dim)
        # self.gap = kwargs.get('gap', Board.gap)



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


# Useless.
# def strip(array:[], value):
#     """
#     Strips all occurences of value within array.
# 
#     :param array: A list containing 'value' any number of times >= 0.
#     :param value: Any object to be excluded from 'array'.
#     :return: 'value'-less 'array'.
#     """
#     return [element for element in array if element != value]


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



def drawGrid(table:[[bool]] or Board, canvas:tk.Canvas, cam_pos:[int,int]):
    """
    Draw each cell of 'table' onto the given 'canvas' with respect to the 'cam_pos' offset.
    The dimensions and other caracteristics of the cells are defined within the Board instance,
    and otherwise (when given a grid instead) make use of the Board class' defaults.
    """

    ### [NOTE] : Using tk's move function would most likely not have been useful,
    ###          as we would've had to compute which parts of the board still had to be drawn.
    canvas.delete(tk.ALL) # canvases actually keep track of all their objects, even when fully drawn over,
                          # so this line is extremely important as to avoid any slow downs

    cell_dim:[int,int] = Board.cell_dim
    gap:[int] = Board.gap
    if type(table) is Board:
        cell_dim = table.cell_dim
        gap = table.gap

    #border_width:int = int(canvas.cget('highlightthickness'))

    for y in range(len(table)):
        if not (-cell_dim[1] < y*(cell_dim[1] + gap[1]) + gap[1] - cam_pos[1] < H): continue
        for x in range(len(table[0])):
            if not (-cell_dim[0] < x * (cell_dim[0] + gap[0]) + gap[0] - cam_pos[0] < W): continue
            canvas.create_rectangle(
                relativeCoordinates(
                    [x*(cell_dim[0] + gap[0]) + gap[0] - cam_pos[0],
                     y*(cell_dim[1] + gap[1]) + gap[1] - cam_pos[1]],
                    cell_dim,
                ),
                fill=["black","white"][table[y][x]],
                outline="",
            )



def liftWindow(win):
    """
    Small utility to ensure the given window ('win') appears immediately and receives focus automatically.
    (since for some reason this is not default behaviour) (it would seem focus stopped working on my machine. How odd.)

    :param win: Tk() object.
    """
    win.lift()
    win.attributes('-topmost', True)
    win.attributes('-topmost', False)
    win.focus_force()



def grid2terminal(table:[[bool]], characters=('⬜','⬛')):
    #[print(con.CURSOR_UP, end=con.CLEAR_LINE) for n in range(len(table))]

    ### [NOTE] : this may not work on older versions of IPython, especially IDE integrated consoles.
    ###          Please prefer standalone terminals, in case you plan to restore this functionality.
    con.clear()
    [print(
        # "  ".join([str(int(item)) for item in line])
        " ".join(
            [characters[item] for item in line]
        )
    ) for line in table]



def toggle(event):
    """
    Toggles the hovered pixel when <RMB> is held.
    """

    ### [NOTE] : (kinda janky, still better than constantly toggling the cell,
    ###          but now *requires* motion to execute, and single clicks have no effect.)

    def pix2cell(pix:int):
        return pix//(BOARD.cell_dim[0]+BOARD.gap[0])

    ### [TODO] : improve this, and this ^^^ which is hardcoded and therefore "*bad*"
    if not (MB_RIGHT and [pix2cell(event.x),pix2cell(event.y)]!=[pix2cell(PREV_CURSOR_POS[n]) for n in range(len(PREV_CURSOR_POS))]): return

    pos = [( (event.x,event.y)[n] + CAM_POS[n]) // (BOARD.cell_dim[n] + BOARD.gap[n] )
           for n in range(2)]
    if [0 <= pos[n] < len((BOARD,BOARD[0])[n]) for n in range(len(pos))] == [True]*2:
        BOARD[pos[1]][pos[0]] ^= 1
    

def drag(event):
    """
    Relies on a global (could not find a better looking yet simple alternative) to store the previous position of the cursor,
    and compare it to the current position.
    This delta is then applied as is to the position of the camera.
    """
    global CAM_POS, PREV_CURSOR_POS
    cursor_pos = [event.x,event.y]

    if MB_LEFT:
        CAM_POS = [CAM_POS[n] - (cursor_pos[n] - PREV_CURSOR_POS[n])
                   for n in range(len(CAM_POS))]
    
    PREV_CURSOR_POS = cursor_pos





def init():
    """
    Called once, before tick().
    Setups everything.
    """

    global WH, W, H, BOARD, IS_RUNNING, WINDOW, CANVAS, CAM_POS, ITERATIONS, MB_LEFT, MB_RIGHT, PREV_CURSOR_POS
    WH = W, H = 256, 256

    board_width = input("Board width [cells] : ")  or W//8
    board_height = input("Board height [cells] : ") or H//8


    ### [TODO] : ConsoleUtil DECORATIONS, dynamic separator length, horizontal line centering
    print('#---------------------------------------------------------#')
    print(f"Press {'<SPACE>'} to pause|unpause, \n"
          f"{'<LEFT-CLICK>'}{'[DRAG]'} to pan the camera, \n"
          f"and {'<RIGHT-CLICK>'}{'[DRAG]'} to place|remove cells.")
    print('#---------------------------------------------------------#')

    BOARD = Board(
        grid(
            int(board_width),
            int(board_height),
            False,
        ),
        gap=[1]*2
    )

    IS_RUNNING = False
    print(f"Simulate State : {'Running' if IS_RUNNING else 'Suspended'}")

    WINDOW = tk.Tk()
    WINDOW.geometry(f"{W}x{H}")
    WINDOW.wm_title("CGOL")
    #WINDOW.wm_resizable(False, False)
    WINDOW.wm_attributes('-toolwindow', True)
    WINDOW.bind('<KeyRelease-space>', lambda event: (
        globals().update(IS_RUNNING=not IS_RUNNING),
        print("Running" if IS_RUNNING else "Paused"),
    ))
    liftWindow(WINDOW)  # jump above all other windows (pin >> unpin)


    ### [NOTE] : a fully functional InputManager would've been a lot of work,
    ###          and may not have been worth the two holdable mouse inputs
    MB_LEFT = False
    WINDOW.bind('<ButtonPress-1>', lambda event: globals().update(MB_LEFT=True))
    WINDOW.bind('<ButtonRelease-1>', lambda event: globals().update(MB_LEFT=False))
    MB_RIGHT = False
    WINDOW.bind('<ButtonPress-3>', lambda event: globals().update(MB_RIGHT=True))
    WINDOW.bind('<ButtonRelease-3>', lambda event: globals().update(MB_RIGHT=False))


    PREV_CURSOR_POS = [0]*2
    CANVAS = tk.Canvas(width=W, height=H, bg="#202020", highlightbackground="#202020")
    CANVAS.bind('<Motion>', lambda event: (
        toggle(event),
        drag(event),
    ))
    WINDOW.bind('<Configure>', lambda event: (
        globals().update(W=event.width,H=event.height),
        CANVAS.configure(width=W,height=H),
    ))
    CANVAS.pack()

    ### [TODO ?] : Camera zoom
    # CAM = OnTheFly(x=0, y=0)
    CAM_POS = [0]*2

    ITERATIONS = 0


def tick():
    """
    Called repeatedly, after init().
    Execute all actions each frame, including drawing the grid,
    refreshing the window, and computing the next iteration of the board.
    """

    global BOARD, ITERATIONS

    while True:

        # temporary way of printing to the terminal
        #grid2terminal(BOARD)

        ITERATIONS += 1
        # console lags like heeeeell
        #print('\r', ITERATIONS, end='', sep='')

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
                # attempt at optimizing large voids, unsure about its effect
                if neighbours==0: continue

                # remove None from the list of the values returned by each rule,
                # only leaving those which would change the state of the current cell
                next_cell = [result for rule in RULES if (result := rule(c=cellState, n=neighbours)) is not None]
                #[(result := rule(c=cellState, n=neighbours)) for rule in RULES if result is not None]
                # REVERSE IT, τ/2

                # set the value of this cell at the next frame to be the last value of the aforementioned list,
                # as precedence is determined this way (corresponds to the order of the functions in RULES).
                next_board[y][x] = (
                    next_cell[-1]
                    if len(next_cell) != 0
                    else BOARD[y][x]
                )

        # we do not assign to BOARD directly as it is not a simple list, it actually contains specific data ;
        # therefore we assign to each of its rows.
        # wont we run into list pointers issues ? we're only copying the first layer
        BOARD[:] = next_board[:] # and finally apply all modifications
                                 # (this is not returned, as this is the `tick()` function).
                                 # (had it been its own function, then it probably would've been returned)
        
        ### [TODO ?] : Simulation Speed
        # sleep(0.25)



if __name__ == '__main__':
    init()
    tick()

