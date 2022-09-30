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

The major experiments for the simulations can be invoked with

```shell
snakemake -c1 run_experiments
```

Adapt the `-c` parameter to specify number of CPU cores to use.

This will run the model according to initial parameters specified in  the model_param.json file 
Tests can be performed with a file at `data/model_runs/trial_run/model_params.json`, with contents:
```json
{
  "run": {
    "simulation_minutes": 80640,
    "snapshot_interval": 30
  },
  "model": {
    "height": 20,
    "width": 20,
    "phosphorus_conc":35,
    "phosphorus_kp":3.5,
     "light_kl":0.1,
     "neighborhood_effect":false,
     
     "grazer_params": {
     "initial_gastropods":0,
      "grazing_rate_percent_of_biomass":2,
      "percent_of_food_to_weight":0.6,
      "init_grazer_biomass":3,
      "max_grazer_biomass":10
      },
    
    "biofilm_params": {
      "growth_rate": 0.0035,
      "max_biomass": 5,
      "initial_biomass_percent": [0,5]
    },
    "clock_params": {
      "step_size": 10
    }
  }
}


```
... or update the snakemake paths as fit for your file setup    