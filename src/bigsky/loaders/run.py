import sys

from bigsky.loaders.utils import init_db
from bigsky.loaders.tycho2 import load_tycho_2


if __name__ == "__main__":
   raw_data_path = sys.argv[1]
   output_filename = sys.argv[2]

   init_db(output_filename)
   load_tycho_2(raw_data_path)
