# -*- coding: utf-8 -*-
from typing import *
import subprocess
import os
from pymkv import MKVFile
import contextlib
from io import BytesIO


class StreamContainer(contextlib.AbstractContextManager):
    """
    A context manager that acts as a video stream.
    Use with `with` for proper cleanup.
    """
    _subs_fn: Optional[str]
    _cmd: List[str]
    _proc_stream: Optional[BytesIO] = None

    def __init__(self, cmd: List[str], subs_fn: Optional[str]):
        self._cmd = cmd
        self._subs_fn = subs_fn

    def __enter__(self):
        (_, self._proc_stream) = subprocess.Popen(self._cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)\
            .communicate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._proc_stream is not None:
            self._proc_stream.close()
        if self._subs_fn is not None:
            try:
                os.remove(self._subs_fn)
            except OSError:
                pass

    def read(self) -> bytes:
        if self._proc_stream:
            raise Exception("Stream not yet opened (use with!)")
        return self._proc_stream.read()


def get_video_clip(vid_fn: str, start_time: str, end_time: str) -> StreamContainer:
    cuda = True  # TODO Determine
    subs_fn, lang = _find_jpn_audio_extract_subs(vid_fn)
    if lang is None:
        amap = '-0:a'
    else:
        amap = '0:a:language:jpn'

    # use our custom ffmpeg
    cmd = ['/home/jasmine/bin/ffmpeg']

    # use our input video,
    # taking video stream zero from the input and doing a direct copy of the japanese audio track
    cmd.extend([
        '-i', vid_fn,
        '-map', '0:v', '-map', amap, '-c:a', 'copy'
    ])

    if subs_fn is not None:
        # if we have subtitles,
        subs_vf = 'copy'
        if subs_fn.endswith(".srt"):
            subs_vf = "subtitles=%s" % (subs_fn,)
        elif subs_fn.endswith(".ass"):
            subs_vf = "ass=%s" % (subs_fn,)
        # add them
        cmd.extend(['-vf', subs_vf])

    if cuda:
        # make sure to encode using nvenc if we have cuda as well
        cmd.extend(['-c:v', 'h264_nvenc'])

    # copy from start time to end time,
    # output format mp4, to standard out
    cmd.extend([
        '-ss', start_time, '-to', end_time,
        '-y', '-f', 'mpegts', '-'
    ])

    return StreamContainer(cmd, subs_fn)


def _find_jpn_audio_extract_subs(vid_fn: str) -> (Optional[str], Optional[int]):
    """
    Gets the japanese audio track ID from the input
    :param vid_fn: Input file
    :return: Filename of extracted subs, The japanese audio track id
    """
    if vid_fn.endswith(".mkv"):
        mkv = MKVFile(vid_fn)
        result_aid = None
        fn = None

        aid = 0
        for track in mkv.get_track():
            if track.track_type == "audio" and result_aid is None:
                if track.language == "jpn":
                    result_aid = aid
                aid += 1
            # language is too screwy, so we go with default here
            # this might have some issues with dual-audio, but we can deal with that later.
            elif track.track_type == "subtitles" and track.language == "jpn":
                if track.track_codec == "S_TEXT/ASS":
                    fn = "subs.ass"
                    track.extract(fn)
                else:
                    raise Exception("Cannot handle subtitle codec %s" % (track.track_codec,))
        return fn, result_aid
    return None
