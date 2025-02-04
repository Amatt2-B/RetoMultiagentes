NO=0    # Inaccessible
RO=1    # Road
SI=2    # Sidewalk
RC=4|RO # Pedestrian crossing (road + crossing)
# BS=8|SI # Bus stop

ND=1 # North
SD=2 # South
ED=4 # East
WD=8 # West

AL=ND|SD|ED|WD # All directions
NE=ND|ED       # North east
SE=SD|ED       # South east
NW=ND|WD       # North west
SW=SD|WD       # South west
BL=ND|SD       # Block (vertical)
IL=ED|WD       # Inline (horizontal)

NT=ND|IL       # North T (nort, east, west)
ST=SD|IL       # South T (south, east, west)
ET=ED|BL       # East T (east, north, south)
WT=WD|BL       # West T (west, north, south)

UP = NT|NE|NW
DOWN = ST|SE|SW
RIGHT = ET|NE|SE
LEFT = WT|NW|SW

DIR_VECS = {
    ND: ( 1, 0),
    SD: (-1, 0),
    ED: ( 0, 1),
    WD: ( 0,-1),
    NE: ( 1, 1),
    SE: (-1, 1),
    NW: ( 1,-1),
    SW: (-1,-1),
}

LIGHT_SHIFT = 16 # Traffic light IDs will start at this bit index
