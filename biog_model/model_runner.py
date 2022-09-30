import time
from tqdm import tqdm
import numpy as np
import xarray as xr
from .model import BiofilmGridModel
from .agents import LogisticBiofilmPatch
from mesa.datacollection import DataCollector


def run_and_return_biomass(run_params: dict, model_params: dict) -> (np.ndarray, float, float):
    print(f'Creating model with {model_params=}')
    model = BiofilmGridModel(**model_params)
    model.create_grid_random()

    print(f'Created model: {model} with {model.height=} & {model.width=} & '
          f'{model.max_biomass=}')


class Simulation:
    def __init__(self, model_params: dict, initial_biomass=None):
        self.model_params = model_params
        self.initial_biomass = initial_biomass

        self._model = None
        self._collector = None
        self._running = False
        self.run_metadata = None

    def create_model(self):
        if self.model is not None:
            raise RuntimeError('Model already created!')

        model = BiofilmGridModel(**self.model_params)

        if self.initial_biomass is not None:
            model.create_grid_from(self.initial_biomass)
        else:
            model.create_grid_random()

        self._model = model

    def create_collector(self):

        def collect_biomass(model):
            data = np.zeros((model.grid.height, model.grid.width))
            for agent in model.agent_scheduler.agents_by_breed[LogisticBiofilmPatch].values():
                # print(agent.pos, agent.biomass)
                x,y = agent.pos
                data[y, x] = agent.biomass

            return data

        collector = DataCollector(
            {
                # "time_step": lambda m: m.agent_scheduler.time,
                "time": lambda m: m.clock.minutes,
                "biomass": collect_biomass
                # "Snail": lambda m: m.schedule.get_breed_count(Snail),
            }
        )
        self._collector = collector

    @property
    def model(self) -> BiofilmGridModel:
        return self._model

    @property
    def collector(self):
        return self._collector

    @property
    def running(self):
        return self._running

    def run(self, simulation_minutes, snapshot_interval):
        if self.running:
            return

        if not self.model:
            self.create_model()
        if not self.collector:
            self.create_collector()

        num_steps = simulation_minutes // (self.model.clock.step_size)

        step_durations = []

        self._running = True
        start_time = time.time()

        # to store initial state
        self.collector.collect(self.model)
        previous_snapshot = self.model.clock.time

        for step_num in tqdm(range(num_steps)):
            tic = time.time()
            self.model.step()
            toc = time.time()
            duration = toc - tic
            step_durations.append(duration)

            # if step_num is zero, snapshot it for initial settings
            # if simtime running, check simtime elapsed since previous snapshot

            simtime = self.model.clock.minutes

            if (simtime - previous_snapshot) >= snapshot_interval:
                self.collector.collect(self.model)
                previous_snapshot = simtime

        end_time = time.time()

        self.run_metadata = dict(
            start_time=start_time,
            durations_mean=np.mean(step_durations),
            durations_std=np.std(step_durations),
            end_time=end_time
        )
        self._running = False

    def get_simulation_data(self) -> xr.Dataset:

        if not self.run_metadata:
            raise RuntimeError('No run data. Has simulation been run fully?')

        collector = self.collector

        simtime = collector.model_vars['time']

        biofilm_biomass = xr.DataArray(
            np.array(collector.model_vars['biomass']),
            dims=('time', 'Y', 'X'),
            coords=dict(
                time=simtime
            ),
        )

        ds = xr.Dataset(dict(
            biofilm_biomass=biofilm_biomass,
        ))
        return ds

    def get_simulation_metadata(self) -> dict:
        return self.run_metadata


def run_simulation(run_params: dict, model_params: dict) -> Simulation:
    sim = Simulation(model_params=model_params)
    sim.run(**run_params)
    return sim


