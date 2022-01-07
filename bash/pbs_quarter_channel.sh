#PBS -S /bin/sh
#PBS -N make-LCs
#PBS -q devel
#PBS -l select=1:ncpus=10:mem=60G:model=ivy
#PBS -l walltime=00:60:00
#PBS -j oe
#PBS -m e
#PBS -V
#PBS -o pfe21:/home4/jimartin/ADAP/kepler-workflow/logs/

# activate conda env
source /nasa/jupyter/4.4/miniconda/etc/profile.d/conda.sh
conda activate kepler-workflow

# project directory
WORKDIR=$(dirname `pwd`)

# change directory
cd "$WORKDIR/kepler_workflow"
echo `pwd`



echo "Channel $ch Quarter $qu"
echo "$bn batches of size $bs"

# lunch parallel jobs
echo "Will run the following command:"
echo "seq 1 ${bn} | xargs -n 1 -I {} -P 10 python make_lightcurves_new.py --quarter ${qu} --channel ${ch} --batch-size ${bs} --batch-number {} --tar-tpfs --tar-lcs --augment-bkg --plot --fit-va --log 20"
seq 1 ${bn} | xargs -n 1 -I {} -P 10 python make_lightcurves_new.py --quarter ${qu} --channel ${ch} --batch-size ${bs} --batch-number {} --tar-tpfs --tar-lcs --augment-bkg --plot --fit-va --log 20

exit 0
