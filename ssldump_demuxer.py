#!/usr/bin/env python

"""Convert an `ssldump` log file with mixed records from multiple connections
to multiple files each with records from a single connection."""

import re
import sys

new_record_p = re.compile("(\d+)\s+(\d+)\s+\d+\.\d+\s+")
prefix = "demux."

def read_ssldump(dump):
    """Return demuxed `streams` read from an ssldump file-like `dump`.
    `streams` is a dictionary:

        {<stream_id>: [<line_or_record>],
         ...}

    `stream_id` 0 is the catch-all stream for plaintext/record-less packets.
    `line` is just a string.
    `record` is a tuple of the form `(<stream_id>, [<lines>])`.
    """
    streams = {0: []}
    current_stream = 0
    current_record = None
    for line in dump:
        m = None
        if line.startswith("New TCP connection #"):
            start = line.find("#")+1
            end = line.find(":", start)
            new_stream = int(line[start:end])
            streams[new_stream] = [line]
        else:
            m = re.match(new_record_p, line)
        if m:
            if current_record:
                stream = current_record[0]
                streams[stream].append(current_record[1])
            current_record = (int(m.group(1)), [line])
        elif line.startswith(" "):
            current_record[1].append(line)
        else:
            streams[0].append(line)
    return streams

def print_streams(streams):
    for stream, stream_items in streams.iteritems():
        with file(prefix + str(stream) + ".log", "w") as f:
            for item in stream_items:
                if type(item) == list:
                    f.write("".join(item))
                else:
                    f.write(item)

def main(args):
    global prefix
    for i in xrange(len(args)):
        if args[i] == "--prefix":
            prefix = args[i+1]
    streams = read_ssldump(sys.stdin)
    print_streams(streams)

if __name__ == '__main__':
    main(sys.argv)
