import os
import glob
import numpy as np
from paths import ARCHIVE_PATH, PACKAGEDIR


def run():

    folder_list = np.sort(glob.glob(f"{ARCHIVE_PATH}/data/kepler/tpf/*"))
    print(len(folder_list))

    for folder in folder_list:
        fname = folder.split("/")[-1]
        table_list = np.sort(
            glob.glob(f"{PACKAGEDIR}/data/support/kepler_tpf_map_{fname}_q*_tar.csv")
        )
        print(f"Folder name {fname} totla tables {len(table_list)}")

        if len(table_list) < 18:
            print("Q avail: ", [x[-10:-8] for x in table_list])


if __name__ == "__main__":

    run()
