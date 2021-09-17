import os
import glob
import argparse
import fitsio
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description="AutoEncoder")
parser.add_argument(
    "--folder",
    dest="folder",
    type=str,
    default="0007",
    help="First level folder name of Kepler archive directory.",
)
parser.add_argument(
    "--quarter",
    dest="quarter",
    type=int,
    default=5,
    help="First level folder name of Kepler archive directory.",
)
parser.add_argument(
    "--path",
    dest="path",
    type=str,
    default="/Users/jorgemarpa/Work/BAERI/ADAP/data/kepler/tpf/Kepler",
    help="Kepler archive path.",
)
parser.add_argument(
    "--batch-size",
    dest="batch_size",
    type=int,
    default=50,
    help="Batch size",
)
parser.add_argument(
    "--concat",
    dest="concat",
    action="store_true",
    default=False,
    help="Concatenate all files.",
)
parser.add_argument(
    "--do-batch",
    dest="do_batch",
    action="store_true",
    default=False,
    help="Computen umber of batches per channel.",
)
args = parser.parse_args()

qd_map = {
    1: 2009166043257,
    2: 2009259160929,
    3: 2009350155506,
    4: 2010078095331,
    5: 2010174085026,
    6: 2010265121752,
    7: 2010355172524,
    8: 2011073133259,
    9: 2011177032512,
    10: 2011271113734,
    11: 2012004120508,
    12: 2012088054726,
    13: 2012179063303,
    14: 2012277125453,
    15: 2013011073258,
    16: 2013098041711,
    17: 2013131215648,
}


def main():

    tpfs = np.sort(
        glob.glob(
            "%s/%s/*/kplr*-%s_lpd-targ.fits.gz"
            % (args.path, args.folder, str(qd_map[args.quarter]))
        )
    )
    print("Total numebr of TPFs in %s: " % (args.folder), tpfs.shape[0])
    if len(tpfs) == 0:
        raise ValueError("No TPFs for selected quarter %i" % args.quarter)

    channels, quarters, ra, dec = np.array(
        [
            [
                fitsio.read_header(f)["CHANNEL"],
                fitsio.read_header(f)["QUARTER"],
                fitsio.read_header(f)["RA_OBJ"],
                fitsio.read_header(f)["DEC_OBJ"],
            ]
            for f in tpfs
        ]
    ).T

    df = pd.DataFrame(
        [tpfs, quarters, channels, ra, dec],
        index=["file_name", "quarter", "channel", "ra", "dec"],
    ).T
    df.channel = df.channel.astype(np.int8)
    df.quarter = df.quarter.astype(np.int8)

    dir_name = "../data/support/"
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    file_name = "%s/kepler_tpf_map_%s_q%02i.csv" % (dir_name, args.folder, args.quarter)
    df.to_csv(file_name)


def concatenate():

    print("Concatenating all lookup tables...")
    f_list = np.sort(
        glob.glob("../data/support/kepler_tpf_map_*_q%02i.csv" % (args.quarter))
    )
    dfs = pd.concat([pd.read_csv(f, index_col=0) for f in f_list], axis=0)
    for f in f_list:
        os.remove(f)

    file_name = "../data/support/kepler_tpf_map_all_q%02i.csv" % (args.quarter)
    dfs.reset_index(drop=True).to_csv(file_name)


def how_many_batches():
    file_name = "../data/support/kepler_tpf_map_all_q%02i.csv" % (args.quarter)
    df = pd.read_csv(file_name, index_col=0)

    channels = np.arange(1, 85)
    number_batch, nsources = [], []
    for ch in channels:
        in_channel = df.query("channel == %i" % ch)
        nsources.append(in_channel.shape[0])
        number_batch.append(int(np.ceil(in_channel.shape[0] / args.batch_size)))
    df_nb = pd.DataFrame(
        np.vstack([channels, nsources, number_batch]).T,
        columns=["channel", "n_sources", "n_batch"],
    )
    # print(df_nb.set_index("channel"))

    file_name = "../data/support/kepler_tpf_nbatches_bs%03i_q%02i.csv" % (
        args.batch_size,
        args.quarter,
    )
    df_nb.set_index("channel").to_csv(file_name)


if __name__ == "__main__":
    if args.concat:
        concatenate()
    elif args.do_batch:
        how_many_batches()
    else:
        main()
    print("Done!")
