# -*- coding: utf-8 -*-
from typing import *
from lxml import etree
import subprocess
import os


class Chapter:
    """
    A chapter in an MKV file. end_time is EOF if there are no subsequent chapters.
    Chapters cannot be nested, despite what the MKV spec says.
    """
    start_time: str
    end_time: str
    display_name: str

    def __init__(self, start_time: str, end_time: str, display_name: str):
        self.start_time = start_time
        self.end_time = end_time
        self.display_name = display_name

    def __repr__(self):
        return "%s (%s - %s)" % (self.display_name, self.start_time, self.end_time)


def get_chapters(filename: str) -> List[Chapter]:
    """
    Returns the chapters from a given MKV file.
    :param filename: The filename of an MKV file
    :return: The chapters in the MKV file
    :raises: Exception if mkvextract fails
    """
    chapters_fn = "%s_chapters.xml" % (filename,)
    # extract out chapters
    subprocess.run(["mkvextract", filename, "chapters", chapters_fn], check=True)
    chapters = []
    # parse chapters file
    try:
        with open(chapters_fn, "rb") as f:
            chapters_doc = etree.parse(f)
            for i, chapter in enumerate(chapters_doc.findall(".//ChapterAtom")):
                start_time = chapter.findtext("./ChapterTimeStart")
                display_name = chapter.findtext("./ChapterDisplay/ChapterString")
                if i > 0:
                    chapters[i-1].end_time = start_time
                chapters.append(Chapter(start_time, 'EOF', display_name))
    except IOError as e:
        if e.errno == 2:  # ENOENT (No such file or directory)
            pass  # no chapters
        else:
            raise e
    # cleanup
    os.remove(chapters_fn)
    return chapters


def get_op_chapter(filename: str) -> Optional[Chapter]:
    """
    Reads the given MKV file to extract out the opening, or None if no opening chapter is found.
    :param filename: MKV file to read
    :return: The chapter, or None if none could be found (ex, does not contain chapters, is not an MKV, ...)
    :raise: Exception if mkvextract fails
    """
    try:
        chapters = get_chapters(filename)
        if len(chapters) > 0:
            print("Found chapters! %s" % (chapters,))
        for chapter in chapters:
            if "OP" == chapter.display_name or "opening" in chapter.display_name.lower():
                return chapter
        return None
    except Exception as e:
        print(e)
        return None
