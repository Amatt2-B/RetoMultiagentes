from enum import Enum
from dataclasses import dataclass
import numpy as np

from model import CityModel
from utils import Encodable

class Commands(Enum):
    START = 'start'
    STEP = 'step'
    STOP = 'stop'

@dataclass
class SimState(Encodable):
    dims: tuple
    agents: list
    grid: list

    @staticmethod
    def fromModel(model: CityModel):
        return SimState(
            dims=model.env.shape,
            agents=model.agents,
            grid=model.env.tiles.tolist(),
        )
