# -*- coding: utf-8 -*-
from typing import *
import random
import socket

from scan import *
import video

#MCAST_IP = "224.1.2.1"
#MCAST_PORT = 8090
#MCAST_TTL = 4  # it's complicated
TCP_PORT = 8091
BUF_SIZE = 4096  # also the packet size for UDP


def handle_http_headers(conn: socket.socket):
    conn.send("HTTP/1.1 200 OK\r\n".encode("utf-8"))
    conn.send("Content-Type: video/mp4\r\n".encode("utf-8"))
    conn.send("Transfer-Encoding: chunked\r\n".encode("utf-8"))
    conn.send("\r\n".encode("utf-8"))


def serve(directory: str):
    (playlist, _) = scan(directory)
    print(playlist)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
        ss.bind(("0.0.0.0", TCP_PORT))
        ss.listen()
        (conn, addr) = ss.accept()
        handle_http_headers(conn)

        while True:
            random.shuffle(playlist)
            for clip in playlist:
                print("Playing %s" % (clip,))
                with video.get_video_clip(clip) as stream:
                    while True:
                        data = stream.read(BUF_SIZE)
                        if not data:
                            break
                        conn.send("%x\r\n".encode("utf-8") % len(data)) # size of chunk
                        conn.sendall(data)
                        conn.send("\r\n".encode("utf-8")) # eoc


if __name__ == "__main__":
    import sys
    serve(sys.argv[1])
