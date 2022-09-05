import matplotlib
matplotlib.use('agg')

rule simulate_model_save_:
    output:
        meta="data/model_runs/{expname}/simulation_metadata.json",
        grids="data/model_runs/{expname}/biomass_data.nc"
    input:
        model_params="data/model_runs/{expname}/model_params.json",
    run:
        import json

        with open(input.model_params) as fp:
            params = json.load(fp)

        run_params = params['run']
        model_params = params['model']
        # print(f'Read in RUN params: {run_params}')

        from biog_model.model_runner import Simulation

        sim = Simulation(model_params=model_params)
        sim.run(**run_params)

        simulation_data = sim.get_simulation_data()
        print(f'Saving simulation data to {output.grids}')
        simulation_data.to_netcdf(output.grids)

        with open(output.meta,'w') as fp:
            json.dump(sim.get_simulation_metadata(),fp,indent=2)


rule simulate_model_fixed_start_:
    output:
        meta="data/model_runs/neighborhood_effect/simulation_metadata.json",
        grids="data/model_runs/neighborhood_effect/biomass_data.nc"
    input:
        model_params="data/model_runs/neighborhood_effect/model_params.json",
        initial_biomass="data/model_runs/neighborhood_effect/initial_biomass.nc"
    run:
        import json
        import xarray as xr
        import numpy as np

        with open(input.model_params) as fp:
            params = json.load(fp)

        biomass = xr.open_dataarray(input.initial_biomass)
        #biomass = np.load(input.initial_biomass)
        print(biomass.shape)
        run_params = params['run']
        model_params = params['model']
        # print(f'Read in RUN params: {run_params}')

        from biog_model.model_runner import Simulation

        sim = Simulation(model_params=model_params, initial_biomass=biomass.data)
        sim.run(**run_params)

        simulation_data = sim.get_simulation_data()
        print(f'Saving simulation data to {output.grids}')
        simulation_data.to_netcdf(output.grids)

        with open(output.meta,'w') as fp:
            json.dump(sim.get_simulation_metadata(),fp,indent=2)


rule neighborhood_effect_:
    output:
        meta="data/model_runs/neighborhood_effect_off/simulation_metadata.json",
        grids="data/model_runs/neighborhood_effect_off/biomass_data.nc"
    input:
        model_params="data/model_runs/neighborhood_effect_off/model_params.json",
        initial_biomass="data/model_runs/neighborhood_effect_off/initial_biomass.nc"
    run:
        import json
        import xarray as xr
        import numpy as np

        with open(input.model_params) as fp:
            params = json.load(fp)

        biomass = xr.open_dataarray(input.initial_biomass)
        #biomass = np.load(input.initial_biomass)
        print(biomass.shape)
        run_params = params['run']
        model_params = params['model']
        # print(f'Read in RUN params: {run_params}')

        from biog_model.model_runner import Simulation

        sim = Simulation(model_params=model_params, initial_biomass=biomass.data)
        sim.run(**run_params)

        simulation_data = sim.get_simulation_data()
        print(f'Saving simulation data to {output.grids}')
        simulation_data.to_netcdf(output.grids)

        with open(output.meta,'w') as fp:
            json.dump(sim.get_simulation_metadata(),fp,indent=2)

rule plot_grid_tseries_mean_:
    output:
        plot = "data/model_runs/{expname}/grid_timeseries_mean.jpg"
    input:
        data = "data/model_runs/{expname}/biomass_data.nc"

    run:
        import xarray as xr
        biomass_grids = xr.open_dataarray(input.data)
        tseries = biomass_grids.mean(dim=('X', "Y"))
        #tseries1 = biomass_grids.std(dim=('X', "Y"))

        import matplotlib.pyplot as plt
        plt.plot(tseries.time/1440, tseries)
        plt.xlabel('Time (days)')
        plt.ylabel('Mean biomass of grid (mg/cm2)')
        plt.savefig(output.plot)

rule plot_grid_tseries_:
    output:
        plot = "data/model_runs/{expname}/grid_timeseries.jpg"
    input:
        data = "data/model_runs/{expname}/biomass_data.nc"

    run:
        import xarray as xr
        biomass_grids = xr.open_dataarray(input.data)
        tseries = biomass_grids.sum(dim=('X', "Y"))

        import matplotlib.pyplot as plt
        plt.plot(tseries.time/1440, tseries)
        plt.xlabel('Time (days)')
        plt.ylabel('Total grid biomass (mg/cm2)')
        plt.savefig(output.plot)



rule plot_grid_maps_:
    output:
        plot="data/model_runs/{expname}/grid_maps.jpg"
    input:
        data="data/model_runs/{expname}/biomass_data.nc"
    run:
        import numpy as np
        import matplotlib.pyplot as plt

        import xarray as xr
        from mpl_toolkits.axes_grid1 import make_axes_locatable

        #num_plots = 4
        biomass_grids = xr.open_dataarray(input.data)
        #tcoord = biomass_grids.time
        #num_tpoints = len(tcoord)
        #selected_tpoints = tcoord[:: num_tpoints // num_plots]
        selected_tpoints = [0, 10080, 20160, 30240, 50400, 80640]

        #print(f'Selected timepoints: {selected_tpoints}')

        biomass_grids_ = biomass_grids.sel(time=selected_tpoints)
        vmin = biomass_grids_.min()
        vmax = biomass_grids_.max()

        fig, axes = plt.subplots(nrows=1,ncols=6,sharex=True,sharey=True,figsize=(15, 6))
        for idx in range(len(axes)):
            tidx = biomass_grids_.time[idx]
            grid_map = biomass_grids_.isel(time=idx)
            #print(f'{idx=} {tidx=} {grid_map.shape=}')
            ax = axes[idx]
            aximg = ax.imshow(grid_map,vmin=vmin,vmax=vmax,interpolation='none')
            ax.set_title(f'day {(tidx.data) / 1440:.1f}',size=20)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right",size="5%",pad=0.05)
        plt.colorbar(aximg,cax=cax).set_label(label='biomass(mg/mm2)',size=12,weight='bold')
        #plt.colorbar()
        fig.tight_layout()
        plt.savefig(output.plot)

rule plot_mean_std_:
    output:
        plot = "data/model_runs/{expname}/mean_std.jpg"
    input:
        data = "data/model_runs/{expname}/biomass_data.nc"

    run:
        import matplotlib.pyplot as plt
        import xarray as xr

        biomass_grids = xr.open_dataarray(input.data)
        biomass_grids.coords['days'] = biomass_grids['time'] / 1440
        plt.figure()
        ax = plt.subplot(111)
        ax2 = plt.twinx(ax)
        lines1 = biomass_grids.mean(dim=('X', "Y")).plot(ax=ax, x='days', color='C0')
        lines2 = biomass_grids.std(dim=('X', "Y")).plot(ax=ax2, x='days', color='C1')
        ax.set_ylabel('Mean biomass of grid (mg/cm2)')
        ax2.set_ylabel('StdDev of biomass (mg/cm2)')
        ax.set_xlabel('Time (days)')
        plt.legend(lines1+lines2, ['Mean', 'Stdev'])

        plt.savefig(output.plot)



rule run_experiments:
    input:
        expand("data/model_runs/{expname}/{files}",
            files=[
                'grid_timeseries.jpg',
                'grid_timeseries_mean.jpg',
                'grid_maps.jpg',
                'mean_std.jpg'
            ],
            expname=[
                #'scenario_kp10/baseline_model',
                'grazing_effect'
                #'try_run',

                #'scenario_kp10/scenario/p100-g0',
                #'scenario_kp10/scenario/p100-g1',
                #'scenario_kp10/scenario/p100-g3',
                #'scenario_kp10/scenario/p100-g6',
                #'scenario_kp10/scenario/p100-g10',
                #'scenario_kp10/scenario/p100-g20',
                #'scenario_kp10/scenario/p100-g25',
                #'scenario_kp10/scenario/p100-g30',
                #'scenario_kp10/scenario/p100-g35',

                #'scenario_kp10/scenario/p5-g0',
                #'scenario_kp10/scenario/p5-g1',
                #'scenario_kp10/scenario/p5-g3',
                #'scenario_kp10/scenario/p5-g6',
                #'scenario_kp10/scenario/p5-g10',
                #'scenario/p5-g10',
                #'scenario_kp10/scenario/p5-g20',
                #'scenario_kp10/scenario/p5-g25',
                #'scenario_kp10/scenario/p5-g30',
                #'scenario_kp10/scenario/p5-g35',
                #'scenario_kp10/scenario/p5-g40',
                #'scenario_kp10/scenario/p10-g0',
                #'scenario_kp10/scenario/p10-g1',
                #'scenario_kp10/scenario/p10-g3',
                #'scenario_kp10/scenario/p10-g6',
                #'scenario_kp10/scenario/p10-g10',
                #'scenario_kp10/scenario/p10-g20',
                #'scenario_kp10/scenario/p10-g25',
                #'scenario_kp10/scenario/p10-g30',
                #'scenario_kp10/scenario/p10-g35',
                #'scenario_kp10/scenario/p10-g40',
                #'scenario_kp10/scenario/p15-g0',
                #'scenario_kp10/scenario/p15-g1',
                #'scenario_kp10/scenario/p15-g3',
                #'scenario_kp10/scenario/p15-g6',
                #'scenario_kp10/scenario/p15-g10',
                #'scenario_kp10/scenario/p15-g20',
                #'scenario_kp10/scenario/p15-g25',
                #'scenario_kp10/scenario/p15-g30',
                #'scenario_kp10/scenario/p15-g35',
                #'scenario_kp10/scenario/p15-g40',
                #'scenario_kp10/scenario/p35-g0',
                #'scenario_kp10/scenario/p35-g1',
                #'scenario_kp10/scenario/p35-g3',
                #'scenario_kp10/scenario/p35-g6',
                #'scenario_kp10/scenario/p35-g10',
                #'scenario_kp10/scenario/p35-g20',
                #'scenario_kp10/scenario/p35-g25',
                #'scenario_kp10/scenario/p35-g30',
                #'scenario_kp10/scenario/p35-g35',
                #'scenario_kp10/scenario/p35-g40',
                #'fixed_start',
                #'scenario_kp10/nutrient_effect_only',
                #'scenario_kp10/light_effect_only',
                #'scenario_kp10/neighborhood_effect',
                #'scenario_kp10/grazing_effect',
                #'scenario_kp10/neighborhood_effect_off',
                #'scenario_kp10/light_and_nutrient_effect',
                #'scenario_kp10/light_and_nutrient_and_neigh',
                #'scenario_kp10/light_and_nutrient_and_neigh+gr',


            ]
        )

