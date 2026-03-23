from graph import Road

class UIRoad:
    road: Road
    visible: bool
    colour: str

    def __init__(self, road: Road, visible: bool, colour: str) -> None:
        self.road = road
        self.visible = visible
        self.colour = colour
