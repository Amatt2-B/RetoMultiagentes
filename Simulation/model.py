import agentpy as ap
import numpy as np

from utils import Encodable

RN = 1 # Road North
RS = 2 # Road South
RE = 3 # Road East
RW = 4 # Road West

SW = 5 # Sidewalk

NL = 0 # Nil

class Agent(ap.Agent, Encodable):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.model: CityModel # Just for typings
        self.agentType = 'agent'

    def toObject(self):
        return {
            'id': self.id,
            'pos': self.getPos(),
            'type': self.agentType,
        }
    
    def getPos(self):
        return self.model.env.positions[self]

class CarAgent(Agent):
    def setup(self):
        self.agentType = 'car'

    def update(self):
        choice = self.model.random.choice(self.model.env.getRoads(self))
        print(self.getPos(), choice)
        self.model.env.move_to(self, choice)

class PedestrianAgent(Agent):
    def setup(self):
        self.agentType = 'pedestrian'

    def update(self):
        sidewalks = self.model.env.getSidewalks(self)
        options = list(
            filter(lambda pos: len(self.model.env.agents[pos]) == 0, sidewalks)
        )

        if len(options):
            choice = self.model.random.choice(self.model.env.getSidewalks(self))
            self.model.env.move_to(self, choice)

class BusAgent(Agent):
    def setup(self):
        self.agentType = 'bus'

    def update(self):
        pass

class CityEnv(ap.Grid):
    def setup(self):
        self.tiles = np.array([
            [SW,SW,SW,SW,RS,RN,SW,SW],
            [RE,RE,RE,RE,RE,RE,RE,RE],
            [RW,RW,RW,RW,RW,RW,RW,RW],
            [SW,SW,SW,SW,RS,RN,SW,SW],
            [SW,SW,SW,SW,RS,RN,SW,NL],
            [NL,NL,NL,SW,RS,RN,SW,NL],
            [NL,NL,NL,SW,RS,RN,SW,NL],
            [NL,NL,NL,SW,RS,RN,SW,NL],
        ])

    def getRoads(self, agent: Agent):
        pos = agent.getPos()

        x1 = max(pos[0] - 1, 0)
        x2 = min(pos[0] + 2, self.tiles.shape[0])

        y1 = max(pos[1] - 1, 0)
        y2 = min(pos[1] + 2, self.tiles.shape[1])

        kernel = self.tiles[x1:x2, y1:y2]

        rows, cols = np.where((0 < kernel) & (kernel < 5))
        rows += x1
        cols += y1
        coords = list(zip(rows, cols))
        return coords
    
    def getSidewalks(self, agent: Agent):
        pos = agent.getPos()

        x1 = max(pos[0] - 1, 0)
        x2 = min(pos[0] + 2, self.tiles.shape[0])

        y1 = max(pos[1] - 1, 0)
        y2 = min(pos[1] + 2, self.tiles.shape[1])

        kernel = self.tiles[x1:x2, y1:y2]

        rows, cols = np.where(kernel == SW)
        rows += x1
        cols += y1
        coords = list(zip(rows, cols))
        return coords

class CityModel(ap.Model):
    def setup(self):
        self.env = CityEnv(self, (8, 8))
        self.agents = [PedestrianAgent(self) for _ in range(10)]

        # rows, cols = np.where((0 < self.env.tiles) & (self.env.tiles < 5))
        rows, cols = np.where(self.env.tiles == SW)

        coords = list(zip(rows, cols))

        agentPos = [self.random.choice(coords) for _ in self.agents]

        self.env.add_agents(self.agents, positions=agentPos)

    def step(self):
        for agent in self.agents:
            agent.update()


