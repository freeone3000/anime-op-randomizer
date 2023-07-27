import os
from chapters import *


def main():
    import sys
    base_dir = sys.argv[1]
    with open("found.txt", "w") as f:
        for dirname in os.listdir(base_dir):
            path = os.path.join(base_dir, dirname)
            if os.path.isdir(path):
                episode = get_representative_episode(path)
                if episode is None:
                    print("No MKV files found for %s" % (path,))
                    continue

                chapter = get_op_chapter(episode)
                if chapter is None:
                    print("No opening found for %s" % (episode,))
                else:
                    print("Opening for %s: %s" % (path, chapter.display_name))
                    f.write("%s: %s (%s - %s)\n" % (episode, chapter.display_name, chapter.start_time, chapter.end_time))


if __name__ == "__main__":
    main()
