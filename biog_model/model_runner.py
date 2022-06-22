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
    # print("making collector")
    # """
    # #Collect total sum of the Grid
    # collector = DataCollector(
    #     {
    #         "Time_step": lambda m: m.schedule.time,
    #         "xrange": lambda m: sum([a.biomass for a in m.schedule.agents_by_breed[Logistic_biofilmPatch].values()]),
    #         "Snail": lambda m: m.schedule.get_breed_count(Snail),
    #     }
    # )
    # """
    # To collect values of biofilm biomass in single cells in the grid
    collector = DataCollector(
        {
            "time_step": lambda m: m.agent_scheduler.time,
            # "biofilm": lambda m: a.biomass for a in m.schedule.get_breed_count[Logistic_biofilmPatch].values())
            "biomass": lambda m: np.array(
                [a.biomass for a in m.agent_scheduler.agents_by_breed[LogisticBiofilmPatch].values()]
            ).reshape(model.height, model.width)
            # "Snail": lambda m: m.schedule.get_breed_count(Snail),

        }
    )

    # print(f"collector={collector}")

    # RUN TIME
    num_days = run_params['simulation_time_days']
    step_duration = run_params['step_duration_minutes']
    snapshot_interval_mins = run_params['snapshot_interval_minutes']

    snapshot_interval_mins = max(snapshot_interval_mins, step_duration)

    total_minutes = num_days * 24 * 60
    num_steps = total_minutes // step_duration

    snapshot_interval = snapshot_interval_mins // step_duration

    step_durations = []
    sim_time_in_minutes = []

    for step_num in tqdm(range(num_steps)):
        tic = time.time()
        model.step()
        toc = time.time()
        duration = toc - tic
        step_durations.append(duration)

        if step_num % snapshot_interval == 0:
            collector.collect(model)
            sim_time = step_num * step_duration
            sim_time_in_minutes.append(sim_time)

    # collector will have a list of 2D arrays. Create a 3D array from these.
    # createa  labeled array from the simulation
    biomass_grids = xr.DataArray(np.array(collector.model_vars['biomass']),
                                 dims=('time', 'Y', 'X'),
                                 coords=dict(
                                     time=sim_time_in_minutes
                                 )
                                 )

    # print(f'My biomass array has {biomass_grids.shape=} {biomass_grids.dtype=}')

    step_durations = np.array(step_durations)
    step_durations_mean = step_durations.mean()
    step_durations_std = step_durations.std()

    return (biomass_grids, step_durations_mean, step_durations_std)


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
        collector = DataCollector(
            {
                # "time_step": lambda m: m.agent_scheduler.time,
                "time": lambda m: m.clock.minutes,
                "biomass": lambda m: np.array(
                    [a.biomass for a in m.agent_scheduler.agents_by_breed[LogisticBiofilmPatch].values()]
                ).reshape(self.model.height, self.model.width)
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
            start_time = start_time,
            durations_mean=np.mean(step_durations),
            durations_std=np.std(step_durations),
            end_time = end_time
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
            biofilm_biomass = biofilm_biomass,
        ))
        return ds

    def get_simulation_metadata(self) -> dict:
        return self.run_metadata

def run_simulation(run_params:dict, model_params:dict) -> Simulation:
    sim = Simulation(model_params=model_params)
    sim.run(**run_params)
    return sim