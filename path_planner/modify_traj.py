import argparse

from src.trajectory import calc_trajectory
from src.ui import paths_from_json
parser = argparse.ArgumentParser(description='Manually generate path data from paths.json')
parser.add_argument('name', type=str, help='name of the path to generate - ie fourball')
args = parser.parse_args()
dir_name = f"paths/{args.name}/"
paths = list(paths_from_json(dir_name))
calc_trajectory(paths, plot=False, name=args.name)
