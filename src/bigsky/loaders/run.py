import sys

from bigsky.loaders.utils import init_db
from bigsky.loaders.tycho1 import load_tycho_1
from bigsky.loaders.tycho2 import load_tycho_2
from bigsky.loaders.ongc import load_ongc
from bigsky.loaders.wds import load_wds


if __name__ == "__main__":
   raw_data_path = sys.argv[1]
   output_filename = sys.argv[2]

   init_db(output_filename)
   load_ongc(raw_data_path)
   load_tycho_1(raw_data_path)
   # load_wds(raw_data_path)

