import pykka
import os
import tomllib
import obfIO as obf

from configIO import global_config

# actionHandler - the main coordinating thread in BLAAC.
# Most things touch this at some point.

# Messages are usually strings coming from input devices.

# Since this program is designed around asynchronicity, this class regularly broadcasts
# its state to the actors it knows about.

class stateHandler(pykka.ThreadingActor):
    def __init__(self, inp_actors, out_actors, board, images={}, sounds={}):
        super().__init__()
        ### handle parameters
        self._board = board
        self._images = images
        self._sounds = sounds
        self._inp_actors = list(inp_actors)
        self._out_actors = dict(out_actors)

    def on_start(self):
        ### set state
        self._focused_row = 0
        self._focused_column = 0
        self._focused_btn = self._board.grid[self._focused_row][self._focused_column]
        self._grid_columns = len(self._board.grid[0])
        self._grid_rows = len(self._board.grid)
        self._sentence = ""

        ### share state with inputs
        state_message = {"grid_dimensions":(self._grid_rows,self._grid_columns)}
        for actor in self._inp_actors:
            actor.tell(state_message)

    def on_failure(self, exception_type, exception_value, traceback):
        print(exception_type)

    def on_receive(self, message):
        if type(message) == tuple:
            #unpack tuples recursively
            for message_ in message:
                self.on_receive(message_)

        match message:
            #FIXME
            case [":ext_BLAAC_load_board", path_or_url]:
                self._board =  obf.board(path_or_url)
                #reset images
            case [":clear", None]:
                self._sentence = ""
            case [command, parameter]:
                logger.warning(f"Statehandler recieved unknown command {command} with parameter {parameter}")
            case sentence:
                self.output(sentence)

    def add_inp_actors(self, inp_actors):
        self._inp_actors.append(inp_actors)

        state_message = {"grid_dimensions":(self._grid_rows,self._grid_columns)}
        for actor in inp_actors:
            actor.tell(state_message)

    def output_text(self, sentence):
        if self._out_actors["speech"] != None:
            self._out_actors["speech"].tell(ProxyCall(
        attr_path=('say',),
        args=(sentence,)
    ))
