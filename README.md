Biofilm Grazers Model
======================

This repo tracks the model definitions and provides tools for running simulations using snakemake.

Installation
--------------
Use conda to create an environment with the dependencies in their latest versions
```shell
conda env create -f requirements.yml
```

To recreate exactly my environment:
```shell
conda env create -f environment.yml
```

Activate it with:
```shell
conda activate biofilm_grazers
```

The Snakefile points to a `data` folder in the same folder. So create a symlink to the data root folder:

```bash
ln -sf ../../path/to/data data  # use -f if you want to force change existing link
```

Running simulations
----------------------

The major experiments for the simulatiosn can be invoked with

```shell
snakemake -c1 run_experiments
```

Adapt the `-c` parameter to specify number of CPU cores to use.

Tests can be performed with a file at `data/model_runs/trial_run/model_params.json`, with contents:
```json
{
  "run": {
    "step_duration_minutes": 120,
    "simulation_time_days": 4,
    "snapshot_interval_minutes": 60
  },
  "model": {
    "height": 130,
    "width": 100,
    "growth_rate":0.25,
    "max_biomass": 0.5
  }
}

```
... or update the snakemake paths as fit for your file setup    