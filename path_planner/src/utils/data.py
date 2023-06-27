import pathlib
import os
import numpy as np

class Data:
    def __init__(self, save_dir: str = "", save_file: str = "path.npy"):
        """
Manage stored data points for re-doing calculations
        :param save_dir: save directory
        :param save_file: save file name
        """
        self.path = pathlib.Path(save_dir, save_file)

    def save_data(self, data: np.array):
        """
Save positions
        :param data: save numpy array
        """
        np.save(str(self.path), data)

    def load_data(self) -> np.array:
        """
Load positions
        :return: np.array of positions
        """
        return np.load(str(self.path))

    def exists(self) -> bool:
        """
Check to see if the data has been created already
        :return: boolean if exists
        """
        return self.path.exists()


def next_path(path_pattern, directory):
    """
    Finds the next free path in an sequentially named list of files

    e.g. path_pattern = 'file-%s.txt':

    file-1.txt
    file-2.txt
    file-3.txt

    Runs in log(n) time where n is the number of existing files in sequence
    """
    i = 1

    # First do an exponential search
    while os.path.exists(directory + path_pattern % i):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2  # interval midpoint
        a, b = (c, b) if os.path.exists(directory + path_pattern % c) else (a, c)

    return path_pattern % b






