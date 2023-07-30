# -*- coding: utf-8 -*-
from typing import *
import subprocess
import os
from pymkv import MKVFile
import contextlib
from io import BytesIO


class Cut(object):
    vid_fn: str
    start_time: Optional[str]
    end_time: Optional[str]

    def __init__(self, vid_fn: str, start_time: Optional[str], end_time: Optional[str]):
        self.vid_fn = vid_fn
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        return "%s (%s - %s)" % (self.vid_fn, self.start_time, self.end_time)

    def to_ffmpeg(self) -> List[str]:
        cmd = []
        if self.start_time is not None:
            cmd.extend(['-ss', self.start_time])
        if self.end_time is not None:
            cmd.extend(['-to', self.end_time])
        return cmd


class StreamContainer(contextlib.AbstractContextManager):
    """
    A context manager that acts as a video stream.
    Use with `with` for proper cleanup.
    """
    _subs_fn: Optional[str]
    _cmd: List[str]
    _proc_stream: subprocess.Popen[bytes] = None

    def __init__(self, cmd: List[str], subs_fn: Optional[str]):
        self._cmd = cmd
        self._subs_fn = subs_fn

    def __enter__(self):
        self._proc_stream = subprocess.Popen(self._cmd,
                                             stdin=subprocess.DEVNULL,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.DEVNULL,
                                             text=False,
                                             universal_newlines=False,
                                             close_fds=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._proc_stream is not None:
            self._proc_stream.stdout.close()
        if self._subs_fn is not None:
            try:
                os.remove(self._subs_fn)
            except OSError:
                pass

    def read(self, b: int = -1) -> bytes:
        if self._proc_stream is None:
            raise Exception("Stream not yet opened (use with!)")
        return self._proc_stream.stdout.read(b)


def get_video_clip(cut: Cut) -> StreamContainer:
    cuda = True  # TODO Determine
    try:
        subs_fn, lang = _find_jpn_audio_extract_subs(cut.vid_fn)
    except ValueError:  # TODO MKVFile is way too strict about BCP47. these are fansubbers :P
        subs_fn = None
        lang = None

    # TODO This fails for ef
    # if lang is None:
    #     amap = '0:a'
    # else:
    #     amap = '0:a:language:jpn'
    amap = '0:a'

    # use our custom ffmpeg
    cmd = ['/home/jasmine/bin/ffmpeg']

    # use our input video,
    # taking video stream zero from the input and doing a direct copy of the japanese audio track
    cmd.extend([
        '-i', cut.vid_fn,
        '-map', '0:v', '-map', amap,
    ])

    # scale to 1080p with side padding
    if cuda:
        subs_vf = 'pad=ih*16/9:ih:(ow-iw)/2:(oh-ih)/2,setsar=1,format=nv12,hwupload_cuda,scale_npp=1920:1080:interp_algo=lanczos'
    else:
        subs_vf = 'pad=ih*16/9:ih:(ow-iw)/2:(oh-ih)/2,setsar=1,scale=1920:1080:interp_algo=lanczos'

    # if we have subtitles, add them to the filter chain *before* scaling
    if subs_fn is not None:
        if subs_fn.endswith(".srt"):
            subs_vf = "subtitles=%s,%s" % (subs_fn, subs_vf)
        elif subs_fn.endswith(".ass"):
            subs_vf += "ass=%s,%s" % (subs_fn, subs_vf)
    cmd.extend(['-vf', subs_vf])

    if cuda:
        # make sure to encode using nvenc if we have cuda as well
        cmd.extend(['-c:v', 'h264_nvenc'])

    # copy from start time to end time,
    # output format mp4, to standard out
    cmd.extend(cut.to_ffmpeg())
    cmd.extend([
        '-y', '-f', 'mpegts', '-'
    ])

    return StreamContainer(cmd, subs_fn)


ASS_FORMATS = ["S_TEXT/ASS", "SubStationAlpha"]  # all the ways we've seen ASS


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
                if track.track_codec in ASS_FORMATS:
                    fn = "subs.ass"
                    track.extract(fn)
                else:
                    raise Exception("Cannot handle subtitle codec %s" % (track.track_codec,))
        return fn, result_aid
    return None
