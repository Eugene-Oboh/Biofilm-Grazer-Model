import matplotlib
matplotlib.use('agg')

rule simulate_model_save_:
    output:
        meta="../../data/model_runs/{expname}/simulation_metadata.json",
        grids="../../data/model_runs/{expname}/biomass_data.nc"
    input:
        model_params="../../data/model_runs/{expname}/model_params.json"

    run:
        import json

        with open(input.model_params) as fp:
            params = json.load(fp)

        run_params = params['run']
        model_params = params['model']
        # print(f'Read in RUN params: {run_params}')

        from biog_model.model_runner import run_and_return_biomass
        biomass_data, durations_mean, duration_std = run_and_return_biomass(
            run_params=run_params,
            model_params=model_params
        )

        # np.save(output.grids,biomass_data)
        biomass_data.to_netcdf(output.grids)
        print(f'Saved biofilm grids to {output.grids}')

        metadict = dict(
            durations_mean=durations_mean,
            durations_std=duration_std,
        )

        with open(output.meta,'w') as fp:
            json.dump(metadict,fp,indent=2)

rule plot_grid_tseries_:
    output:
        plot = "../../data/model_runs/{expname}/grid_timeseries.jpg"
    input:
        data = "../../data/model_runs/{expname}/biomass_data.nc"

    run:
        import xarray as xr
        biomass_grids = xr.open_dataarray(input.data)
        tseries = biomass_grids.mean(dim=('X', "Y"))

        import matplotlib.pyplot as plt
        plt.plot(tseries.time, tseries)
        plt.xlabel('Time (min)')
        plt.ylabel('Mean biomass (mg/mm2)')
        plt.savefig(output.plot)



rule plot_grid_maps_:
    output:
        plot="../../data/model_runs/{expname}/grid_maps.jpg"
    input:
        data="../../data/model_runs/{expname}/biomass_data.nc"
    run:
        import numpy as np
        import matplotlib.pyplot as plt

        import xarray as xr

        num_plots = 4
        biomass_grids = xr.open_dataarray(input.data)
        tcoord = biomass_grids.time
        num_tpoints = len(tcoord)
        selected_tpoints = tcoord[:: num_tpoints// num_plots ]

        print(f'Selected timepoints: {selected_tpoints}')

        biomass_grids_ = biomass_grids.sel(time=selected_tpoints)
        vmin = biomass_grids_.min()
        vmax = biomass_grids_.max()


        fig, axes = plt.subplots(nrows=1, ncols=4, sharex=True, sharey=True)

        for idx in range(len(axes)):
            tidx = biomass_grids_.time[idx]
            grid_map = biomass_grids_.isel(time=idx)
            print(f'{idx=} {tidx=} {grid_map.shape=}')
            ax = axes[idx]
            aximg = ax.imshow(grid_map, vmin=vmin, vmax=vmax)
            ax.set_title(f'{float(tidx.data):.1f} min')


        plt.colorbar(aximg)
        plt.xlabel('dimension')
        plt.ylabel('dimension')
        fig.tight_layout()
        plt.savefig(output.plot)


rule plot_mean_std_:
    output:
        plot = "../../data/model_runs/{expname}/mean_std.jpg"
    input:
        data = "../../data/model_runs/{expname}/biomass_data.nc"

    run:
        import matplotlib.pyplot as plt
        import xarray as xr

        biomass_grids = xr.open_dataarray(input.data)

        # TODO: use plt.twinx or subplots to separate mean & std plots
        
        plt.figure()
        ax = plt.subplot(111)
        ax2 = plt.twinx(ax)
        lines1 = biomass_grids.isel(X=slice(5,15),Y=slice(5,15)).mean(['X', 'Y']).plot(ax=ax, color='C0')
        lines2 = biomass_grids.isel(X=slice(5,15),Y=slice(5,15)).std(['X', 'Y']).plot(ax=ax2, color='C1')
        ax.set_ylabel('Mean of biomass (mg/mm2)')
        ax2.set_ylabel('StdDev of biomass (mg/mm2)')
        plt.xlabel('Time (min)')
        plt.legend(lines1+lines2, ['Mean', 'Stdev'])
        plt.savefig(output.plot)


rule run_experiments:
    input:
        expand("../../data/model_runs/{expname}/{files}",
            files=[
                'grid_timeseries.jpg',
                'grid_maps.jpg',
                'mean_std.jpg'
            ],
            expname=[
                'try_run',
                # 'base/line_model'
                #'stochastic_start',
            ]
        )