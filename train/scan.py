import os
from chapters import *
from anime import *
from video import *


def scan(base_dir: str) -> (List[Cut], List[str]):
    """
    Returns the list of good entries (with cuts) and bad entries (dir names)
    :return: (good, bad)
    """
    import sys
    good = []
    bad = []
    for dirname in os.listdir(base_dir):
        path = os.path.join(base_dir, dirname)
        if os.path.isdir(path):
            separate_ops = get_separate_ops(path)
            if len(separate_ops) != 0:
                for op in separate_ops:
                    print("Opening for %s: %s" % (path, op))
                    good.append(Cut(op, None, None))
            else:
                episode = get_representative_episode(path)
                if episode is None:
                    bad.append(path)
                    continue

                chapter = get_op_chapter(episode)
                if chapter is None:
                    bad.append(path)
                else:
                    good.append(Cut(episode, chapter.start_time, chapter.end_time))
    return good, bad
