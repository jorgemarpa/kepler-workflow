#PBS -S /bin/sh
#PBS -N make-LCs
#PBS -q normal
#PBS -l select=1:ncpus=10:mem=60G:model=ivy
#PBS -l walltime=06:00:00
#PBS -j oe
#PBS -m e
#PBS -V
#PBS -o pfe21:/home4/jimartin/ADAP/kepler-workflow/logs/

# activate conda env
source /nasa/jupyter/4.4/miniconda/etc/profile.d/conda.sh
conda activate kepler-workflow

echo `which python`

# project directory
WORKDIR=$(dirname `pwd`)

# get batch info from quarter file
info="${WORKDIR}/data/support/fail_batch_index_quarter${quarter}_${idx}.dat"
totallines=`cat "$info" | wc -l | sed 's/^ *//g'`

# change directory
cd "$WORKDIR/kepler_workflow"
echo `pwd`

echo "Quarter $quarter"
echo "Total failed batches in quarter $totallines"

# lunch parallel jobs
echo "Will run the following command:"
echo "cat ${info} | xargs -n 1 -I {} -P 10 python make_lightcurves.py --quarter ${quarter} --batch-index {} --tar-tpfs --tar-lcs --fit-va --use-cbv --augment-bkg --iter-neg --save-arrays feather --log 20"
cat ${info} | xargs -n 1 -I {} -P 10 python make_lightcurves.py --quarter ${quarter} --batch-index {} --tar-tpfs --tar-lcs --fit-va --use-cbv --augment-bkg --iter-neg --save-arrays feather --log 20

exit 0
