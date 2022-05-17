import os
import glob
import shutil
import tarfile
import argparse
import fitsio
import shutil
import tempfile
from tqdm import tqdm
import numpy as np

from paths import *


def do_archive(quarter, channel, bkg=False, augment_bkg=False, fit_va=True):

    print(
        f"{LCS_PATH}/kepler/ch{channel:02}/q{quarter:02}/"
        f"kbonus-kepler-bkg_ch{channel:02}_q{quarter:02}_v1.0_lc_*_"
        "poscorr_sqrt_tk6_tp100_fvaT_bkgT_augT.tar.gz"
    )
    tar_files = sorted(
        glob.glob(
            f"{LCS_PATH}/kepler/ch{channel:02}/q{quarter:02}/"
            f"kbonus-kepler-bkg_ch{channel:02}_q{quarter:02}_v1.0_lc_*_"
            "poscorr_sqrt_tk6_tp100_fvaT_bkgT_augT.tar.gz"
        )
    )
    print(f"Total tar files: {len(tar_files)}")

    for i, tf in enumerate(tar_files):
        print(f"Working with file {i+1}/{len(tar_files)}: {tf}")
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(tf) as tar:
                members = tar.getmembers()
                labels = [x.name.split("/")[-1].split("_")[4][:-4] for x in members]

                ids = [
                    f"{int(x.split('-')[-1]):09}"
                    if x.startswith("KIC")
                    else x.split("-")[-1]
                    for x in labels
                ]
                dirs = list(set([x[:4] for x in ids]))
                print("Creating the following directories:")
                print(dirs)

                for dir in dirs:
                    dir_path = f"{LCS_PATH}/kepler/{dir}"
                    if not os.path.isdir(dir_path):
                        os.makedirs(dir_path)

                for k, member in tqdm(
                    enumerate(members),
                    total=len(members),
                    desc="Extracting FITS into archive",
                ):
                    if not bkg:
                        dirout = f"{LCS_PATH}/kepler/{ids[k][:4]}/{ids[k]}"
                    else:
                        dirout = f"{LCS_PATH}/kepler-bkg/{ids[k][:4]}/{ids[k]}"
                    if not os.path.isdir(dirout):
                        os.makedirs(dirout)
                    fout = f"{dirout}/{member.name}"
                    if os.path.isfile(fout):
                        tar.extract(member, path=tmpdir)
                        shutil.copy(
                            f"{tmpdir}/{member.name}",
                            fout.replace("_lc.fits", "_lc_2.fits"),
                        )
                    else:
                        tar.extract(member, path=dirout)


def rename_fits():
    dir_list = sorted([x.path for x in os.scandir(f"{LCS_PATH}/kepler/") if x.is_dir()])
    dir_list = [x for x in dir_list if not x.split("/")[-1].startswith("ch")]

    for dir in tqdm(dir_list, desc="Renaming files (dir iter)"):
        subdir_list = sorted([x.path for x in os.scandir(dir) if x.is_dir()])
        for subdir in subdir_list:
            files = glob.glob(f"{subdir}/hlsp_kbonus-bkg_kepler_kepler*.fits")
            for f in files:
                if "KIC" in f or "kic" in f:
                    path, fname = os.path.split(f)
                    label = fname.split("_")[4][:-4]
                    kic = int(label.split("-")[1])
                    newname = fname.replace(label, f"kic-{kic:09}")
                    shutil.move(f, f"{path}/{newname}")
                else:
                    path, fname = os.path.split(f)
                    shutil.move(f, f"{path}/{fname.lower()}")


def drop_duplicates(dir, bkg=False, augment_bkg=False, fit_va=True):
    print(f"Working on {dir}")
    if not bkg:
        dupfiles = glob.glob(
            f"{LCS_PATH}/kepler/{dir}/*/hlsp_kbonus-bkg_kepler_kepler*_lc_2.fits"
        )
    else:
        dupfiles = glob.glob(
            f"{LCS_PATH}/kepler-bkg/{dir}/*/hlsp_kbonus-bkg_kepler_kepler*_lc_2.fits"
        )
    if len(dupfiles) == 0:
        print("No duplicated files")
        return
    for sec in dupfiles:
        fir = sec.replace("_lc_2.fits", "_lc.fits")
        err_means = [
            fitsio.read(fir, ext=1, columns="FLUX_ERR").mean(),
            fitsio.read(sec, ext=1, columns="FLUX_ERR").mean(),
        ]
        if np.isnan(err_means).all():
            err_means = [
                fitsio.read(fir, ext=1, columns="SAP_FLUX_ERR").mean(),
                fitsio.read(sec, ext=1, columns="SAP_FLUX_ERR").mean(),
            ]
        if np.isnan(err_means).all():
            continue
        print(err_means)
        if (np.array(err_means) == 0).all():
            print("All empty lcs, removing both...")
            os.remove(fir)
            os.remove(sec)
        elif np.nanargmin(err_means) == 0:
            print("keep 1")
            os.remove(sec)
        elif np.nanargmin(err_means) == 1:
            print("keep 2")
            os.remove(fir)
            shutil.move(sec, fir)
        else:
            continue
        print("----" * 5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quarter",
        dest="quarter",
        type=int,
        default=None,
        help="Quarter number.",
    )
    parser.add_argument(
        "--channel",
        dest="channel",
        type=int,
        default=None,
        help="Channel number",
    )
    parser.add_argument(
        "--dir",
        dest="dir",
        type=int,
        default=None,
        help="Kepler 4-digit directory",
    )
    parser.add_argument(
        "--bkg",
        dest="bkg",
        action="store_true",
        default=True,
        help="PSFMachine fitted the bkg",
    )
    args = parser.parse_args()
    if args.quarter and args.channel:
        do_archive(args.quarter, args.channel, bkg=args.bkg, augment_bkg=args.bkg)

    # rename_fits()
    if args.dir:
        drop_duplicates(args.dir, bkg=args.bkg, augment_bkg=args.bkg)
