import agentpy as ap
import numpy as np

from utils import Encodable

class Agent(ap.Agent, Encodable):
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
        self.model: CityModel
        self.agentType = 'car'

    def update(self):
        choice = self.model.random.choice([(0,1), (1,0), (0,-1), (-1,0)]);
        self.model.env.move_by(self, choice)

class CityEnv(ap.Grid):
    def setup(self):
        self.tiles = np.zeros(shape=self.grid.shape)

class CityModel(ap.Model):
    def setup(self):
        self.env = CityEnv(self, (20, 20))
        self.agents = [CarAgent(self) for _ in range(10)]
        self.env.add_agents(self.agents, random=True)

    def step(self):
        for agent in self.agents:
            agent.update()


