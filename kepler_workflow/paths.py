import os
import socket

PACKAGEDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

if socket.gethostname() == "NASAs-MacBook-Pro.local":
    ARCHIVE_PATH = "/Users/jorgemarpa/Work/BAERI/ADAP"
    OUTPUT_PATH = f"{PACKAGEDIR}/data"
    LCS_PATH = f"{PACKAGEDIR}/data/lcs"

else:
    ARCHIVE_PATH = "/nobackup/jimartin/ADAP"
    OUTPUT_PATH = f"{PACKAGEDIR}/data"
    LCS_PATH = "/nobackup/jimartin/ADAP/kbonus/lcs"
