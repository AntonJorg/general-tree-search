#!/bin/sh
### General options
### -- specify queue --
#BSUB -q hpc
### -- set the job Name --
#BSUB -J GTS_Test
### -- ask for number of cores (default: 1) --
#BSUB -n 9
### -- specify that the cores must be on the same host --
#BSUB -R "span[hosts=1]"
### -- set per core memory limit -- 
#BSUB -R "rusage[mem=1GB]"
### -- request specific cpu model --
#BSUB -R "select[model == XeonE5_2660v3]"
### -- per core memory limit (job is killed if exceeded) --
#BSUB -M 2GB
### -- set walltime limit: hh:mm --
#BSUB -W 48:00
### -- set the email address --
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
#BSUB -u aj@antonjorg.com
### -- send notification at start --
#BSUB -B
### -- send notification at completion --
#BSUB -N
### -- Specify the output and error file. %J is the job-id --
### -- -o and -e mean append, -oo and -eo mean overwrite --
#BSUB -o Output_%J.out
#BSUB -e Output_%J.err

# main program

python -m uv run experiments/experiment_agent_search.py --search-time 1.0 --n-games 250 --n-workers 8