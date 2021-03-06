import os
import glob
import argparse
import numpy as np
import pandas as pd
import lightkurve as lk
import fitsio
from tqdm import tqdm

from paths import *


def main(dir, quarter):
    print(f"Working on {dir}")
    lcfs = glob.glob(
        f"{LCS_PATH}/kepler/{dir}/*/hlsp_kbonus-bkg_kepler_kepler*_lc.fits"
    )
    print(len(lcfs))
    kics, gids = [], []
    ras, decs = [], []
    column, row = [], []
    sap_flux, sap_flux_err = [], []
    psf_flux, psf_flux_err = [], []
    FLFRCSAP, CROWDSAP, NPIXSAP = [], [], []
    channel = []
    gmag, rpmag, bpmag = [], [], []

    for k, f in tqdm(enumerate(lcfs), total=len(lcfs), desc="FITS"):
        gids.append(fitsio.read_header(f)["GAIAID"])
        kics.append(fitsio.read_header(f)["KEPLERID"])
        ras.append(fitsio.read_header(f)["RA_OBJ"])
        decs.append(fitsio.read_header(f)["DEC_OBJ"])
        column.append(fitsio.read_header(f)["COLUMN"])
        row.append(fitsio.read_header(f)["ROW"])
        FLFRCSAP.append(fitsio.read_header(f)["FLFRCSAP"])
        CROWDSAP.append(fitsio.read_header(f)["CROWDSAP"])
        NPIXSAP.append(fitsio.read_header(f)["NPIXSAP"])
        channel.append(fitsio.read_header(f)["CHANNEL"])
        gmag.append(fitsio.read_header(f)["GMAG"])
        rpmag.append(fitsio.read_header(f)["RPMAG"])
        bpmag.append(fitsio.read_header(f)["BPMAG"])

        sap_flux.append(np.nanmedian(fitsio.read(f, ext=1, columns="SAP_FLUX")))
        psf_flux.append(np.nanmedian(fitsio.read(f, ext=1, columns="FLUX")))

        nt = fitsio.read_header(f, ext=1)["NAXIS2"]
        sap_flux_err.append(
            np.sqrt(np.nansum(fitsio.read(f, ext=1, columns="SAP_FLUX_ERR") ** 2)) / nt
        )
        psf_flux_err.append(
            np.sqrt(np.nansum(fitsio.read(f, ext=1, columns="FLUX_ERR") ** 2)) / nt
        )

    df = pd.DataFrame.from_dict(
        {
            "kic": kics,
            "gaia_designation": gids,
            "ra": ras,
            "dec": decs,
            "column": column,
            "row": row,
            "sap_flux": sap_flux,
            "sap_flux_err": sap_flux_err,
            "psf_flux": psf_flux,
            "psf_flux_err": psf_flux_err,
            "gmag": gmag,
            "rpmag": rpmag,
            "bpmag": bpmag,
            "channel": channel,
            "flfrcsap": FLFRCSAP,
            "crowdsap": CROWDSAP,
            "npixsap": NPIXSAP,
        }
    )
    dirname = f"{PACKAGEDIR}/data/catalogs/tpf/"
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    df.to_csv(
        f"{PACKAGEDIR}/data/catalogs/tpf/kbonus_catalog_q{quarter:02}_dir{dir}.csv"
    )


def concat_dir_catalogs(quarter):
    files = glob.glob(
        f"{PACKAGEDIR}/data/catalogs/tpf/kbonus_catalog_q{quarter:02}_dir*.csv"
    )

    df = pd.concat([pd.read_csv(x) for x in files])

    df.reset_index(drop=True).drop("Unnamed: 0", axis=1).to_csv(
        f"{PACKAGEDIR}/data/catalogs/tpf/kbonus_catalog_q{quarter:02}.csv"
    )


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
        "--dir",
        dest="dir",
        type=str,
        default=None,
        help="Kepler 4-digit directory",
    )
    parser.add_argument(
        "--concat",
        dest="concat",
        action="store_true",
        default=False,
        help="Concatenate dir catalogs.",
    )
    args = parser.parse_args()

    if args.concat:
        concat_dir_catalogs(args.quarter)
    else:
        main(args.dir, args.quarter)
