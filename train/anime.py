# -*- coding: utf-8 -*-
"""
Encodes knowledge about folder structures for scene releases of anime.
"""
from typing import *
import os


def get_representative_episode(dirname: str) -> Optional[str]:
    """
    Gets a representative file (not the first, not the last, etc) from a directory
    containing anime files. MUST be an MKV.
    :param dirname: The directory containing anime files
    :return: A representative episode filename
    """
    files = [x for x in os.listdir(dirname) if x.endswith(".mkv")]
    if len(files) == 0:
        return None
    files.sort()
    return os.path.join(dirname, files[len(files) // 2])


def get_separate_ops(dirname: str) -> List[str]:
    """
    Gets the separated OP files out of the directory, preferring creditless
    :param dirname:
    :return:
    """
    files = [fn for fn in os.listdir(dirname) if fn.endswith(".mkv") and "OP" in fn]
    if len(files) == 0:
        return []  # return quickly if there are no OPs

    has_creditless = False
    clean_names = ["Creditless", "Clean", "NCOP"]
    for fn in files:
        for clean_name in clean_names:
            if clean_name in fn:
                has_creditless = True
                break
    filtered_files = []
    if has_creditless:
        for fn in files:
            for clean_name in clean_names:
                if clean_name in fn:
                    filtered_files.append(os.path.join(dirname, fn))
                    break
    else:
        filtered_files = [os.path.join(dirname, fn) for fn in files]
    return filtered_files
