# -*- coding: utf-8 -*-
from typing import *
import subprocess
import os
from pymkv import MKVFile

def cut_video(vid_fn: str, start_time: str, end_time: str) -> str:
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
    # output format mp4, to standard out (TODO should not be standard out)
    cmd.extend([
        '-ss', start_time, '-to', end_time,
        '-y', '-f', 'mpegts', '-'
    ])
    # cleanup
    if subs_fn is not None:
        os.remove(subs_fn)


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
