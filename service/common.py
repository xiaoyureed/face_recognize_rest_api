import os.path as path
import os

from config import consts


def show_dataset():
    result = []
    file_names = os.listdir(consts.dataset_path)
    for f_name in file_names:
        (f_name_pure, _) = path.splitext(f_name)
        result.append(f_name_pure)
    return result
