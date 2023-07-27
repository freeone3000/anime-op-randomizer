import os
from chapters import *
from anime import *


def main():
    import sys
    base_dir = sys.argv[1]
    with open("bad.txt", "w") as badf:
        with open("found.txt", "w") as f:
            for dirname in os.listdir(base_dir):
                path = os.path.join(base_dir, dirname)
                if os.path.isdir(path):
                    separate_ops = get_separate_ops(path)
                    if len(separate_ops) != 0:
                        for op in separate_ops:
                            print("Opening for %s: %s" % (path, op))
                            f.write("%s\n" % (op,))
                    else:
                        episode = get_representative_episode(path)
                        if episode is None:
                            badf.write("%s\n" % (path,))
                            continue

                        chapter = get_op_chapter(episode)
                        if chapter is None:
                            badf.write("%s\n" % (path,))
                        else:
                            print("Opening for %s: %s" % (path, chapter.display_name))
                            f.write("%s: %s (%s - %s)\n" % (episode, chapter.display_name, chapter.start_time, chapter.end_time))


if __name__ == "__main__":
    main()
