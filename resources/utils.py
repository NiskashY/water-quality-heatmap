import os


def get_path_for_saving() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path