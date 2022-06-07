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
            "time_step": lambda m: m.schedule.time,
            # "biofilm": lambda m: a.biomass for a in m.schedule.get_breed_count[Logistic_biofilmPatch].values())
            "biomass": lambda m: np.array(
                [a.biomass for a in m.schedule.agents_by_breed[LogisticBiofilmPatch].values()]
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
