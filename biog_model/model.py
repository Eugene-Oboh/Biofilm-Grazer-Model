import random
import typing as T
from dataclasses import dataclass

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from .agents import Gastropods, LogisticBiofilmPatch
from .schedule import RandomActivationByBreed
from .environment import Illumination


@dataclass
class BIOFILM_PARAMS:
    growth_rate: float = 0.0048  # per 10 minutes
    max_biomass: float = 0.5,  # mg/mm2
    initial_biomass_percent: T.Tuple[float, float] = (0, 5)  # in percentage of max_biomass

class GRAZER_PARAMS:
    def __init__(self, initial_gastropods=0, init_grazer_biomass=0, grazing_rate_percent_of_biomass=0, percent_of_food_to_weight=0, max_grazer_biomass=0):
        self.initial_gastropods = initial_gastropods
        self.init_grazer_biomass = init_grazer_biomass
        self.grazing_rate_percent_of_biomass = grazing_rate_percent_of_biomass
        self.percent_of_food_to_weight = percent_of_food_to_weight
        self.max_grazer_biomass = max_grazer_biomass


class Clock:
    """
    This is the model's simulation clock

    It tracks minutes elapsed in simulation time, and increments it in some step size.
    """

    def __init__(self, initial_time=0, step_size=1):
        self.time = initial_time  # minutes elapsed
        self.step_size = step_size

    def increment(self):
        self.time += self.step_size

    def reset(self):
        self.time = 0

    @property
    def hours(self):
        return self.time / 60

    @property
    def minutes(self):
        return self.time


class BiofilmGridModel(Model):

    def __init__(
            self,
            *args,

            neighborhood_effect=True,
            phosphorus_conc=35,
            phosphorus_kp=10,
            light_kl=0.1,
            height=20,
            width=20,
            clock_params=None,
            light_params=None,
            biofilm_params=None,
            grazer_params=None,
            biofilm=True,

            **kwargs
    ):
        """
        Create a new biog model with the given parameters.
        """
        super().__init__(*args, **kwargs)

        # Set parameters
        self.neighborhood_effect = neighborhood_effect
        self.light_kl = light_kl
        self.phosphorus_conc = phosphorus_conc
        self.phosphorus_kp = phosphorus_kp
        self.height = height
        self.width = width
        self.biofilm = biofilm

        clock_params = clock_params or {}
        self.clock = Clock(**clock_params)

        biofilm_params = biofilm_params or {}
        self.biofilm_params = BIOFILM_PARAMS(**biofilm_params)

        grazer_params = grazer_params or {}
        self.grazer_params = GRAZER_PARAMS(**grazer_params)


        light_params = light_params or {}
        self.illumination = Illumination(**light_params)

        self.agent_scheduler = RandomActivationByBreed(self)
        self.grid = MultiGrid(height=self.height, width=self.width, torus=False)

        # Create Gastropods:
        for i in range(self.grazer_params.initial_gastropods):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            gastropods = Gastropods(self.next_id(), (x, y), self, True, 0, self.grazer_params.grazing_rate_percent_of_biomass,
                                    self.grazer_params.init_grazer_biomass, self.grazer_params.percent_of_food_to_weight, self.grazer_params.max_grazer_biomass)
            self.grid.place_agent(gastropods, (x, y))
            self.agent_scheduler.add(gastropods)

    def create_grid_random(self):
        bparams = self.biofilm_params
        # create biofilm patch
        for agent, x, y in self.grid.coord_iter():
            init_biomass_low, init_biomass_high = [v / 100 * bparams.max_biomass for v in
                                                   bparams.initial_biomass_percent]
            initial_biomass = random.uniform(init_biomass_low, init_biomass_high)

            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=bparams.max_biomass,
                initial_biomass=initial_biomass,
                growth_rate=bparams.growth_rate,
            )
            self.grid.place_agent(patch, (x, y))
            self.agent_scheduler.add(patch)


    def create_grid_from(self, data: np.ndarray):
        bparams = self.biofilm_params

        grid_shape = (self.grid.height, self.grid.width)
        if grid_shape != data.shape:
            raise ValueError(f'Given {data.shape=} does not match grid shape ({grid_shape=})')

        for agent, x, y in self.grid.coord_iter():
            initial_biomass = data[y, x]
            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=bparams.max_biomass,
                initial_biomass=initial_biomass,
                growth_rate=bparams.growth_rate
            )
            self.grid.place_agent(patch, (x, y))
            self.agent_scheduler.add(patch)

    def step(self):
        """
        Each step of the model should do the following:

        - increment the clock
        - step all the agents (using self.agent_schedule.step())
        """
        self.clock.increment()
        self.agent_scheduler.step()  # this updates all agents in order of agent class(?)



