import pykka

# actionHandler - the main coordinating thread in BLAAC.
# Most things touch this at some point.

# Messages are usually strings coming from input devices.

# Since this program is designed around asynchronicity, this class regularly broadcasts
# its state to the actors it knows about.

class stateHandler(pykka.ThreadingActor):
    def __init__(self, inp_actors, out_actors, board, images={}, sounds={}):
        ### handle parameters
        self._board = board
        self._images = images
        self._sounds = sounds
        self._inp_actors = inp_actors
        self._out_actors = out_actors

    def on_start():
        ### set state
        self._focused_row = 0
        self._focused_column = 0
        self._focused_btn = self.board.grid[focus_row][focus_column]
        self._grid_width = len(self.board.grid[0])
        self._grid_height = len(self.board.grid)

        ### share state with inputs
        state_message = {"grid_dimensions":(self._grid_width,self._grid_height)}
        for actor in inp_actors:
            actor.tell(state_message)

