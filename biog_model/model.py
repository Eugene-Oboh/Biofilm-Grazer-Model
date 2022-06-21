import random

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from .agents import LogisticBiofilmPatch
from .schedule import RandomActivationByBreed

class ModelClock:
    def __init__(self, step_size, day_length, night_length):
        self.time = 0
        self.step_size = step_size
        self.day_length = day_length
        self.night_length = night_length
        ...


    def increment(self):
        self.time += self.step_size
        ...

class BiofilmGridModel(Model):

    def __init__(
            self,
            *args,

            phosphorus_conc = 25,
            phosphorus_kp =3.5,
            phosphorus_umax =0.0031,
            height=20,
            width=20,
            growth_rate=0.0031,
            max_biomass=0.5,
            initial_biomass_percent=(0, 5),  # in percentage of max_biomass
            **kwargs
    ):
        """
        Create a new bng model with the given parameters.
        """
        super().__init__(*args, **kwargs)

        # Set parameters
        self.phosphorus_umax =phosphorus_umax
        self.phosphorus_kp = phosphorus_kp
        self.phosphorus_conc = phosphorus_conc

        self.height = height
        self.width = width
        self.growth_rate = growth_rate
        self.max_biomass = max_biomass
        self.initial_biomass_percent = initial_biomass_percent

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(height=self.height, width=self.width, torus=False)

        self.clock = ModelClock(step_size=10, day_length=12*60, night_length=12*60)



    def create_grid_random(self):

        # create biofilm patch
        for agent, x, y in self.grid.coord_iter():
            init_biomass_low, init_biomass_high = [v / 100 * self.max_biomass for v in self.initial_biomass_percent]
            initial_biomass = random.uniform(init_biomass_low, init_biomass_high)


            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=self.max_biomass,
                initial_biomass=initial_biomass,
                growth_rate=self.growth_rate
            )

            self.grid.place_agent(patch, (x, y))
            self.schedule.add(patch)

    data = np.random.uniform(0.00, 0.005, [20, 20])
    data[2:5] = 0
    def create_grid_from(self, data: np.ndarray):

        grid_shape = (self.grid.width, self.grid.height)
        if grid_shape != data.shape:
            raise ValueError(f'Given {data.shape=} does not match grid shape ({grid_shape=})')

        for agent, x, y in self.grid.coord_iter():
            initial_biomass = data[y, x]
            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=self.max_biomass,
                initial_biomass=initial_biomass,
                growth_rate=self.growth_rate
            )
            self.grid.place_agent(patch, (x, y))
            self.schedule.add(patch)

    def step(self):
        self.clock.increment()
        self.schedule.step()
