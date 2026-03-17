class Npc:
    def __init__(self, attached_gui, dialogues: list, pos: tuple, type: str):
        self.gui = attached_gui
        self.type = type
        self.dialogues = dialogues
        self.pos = pos
        self.recruited = False