#!/usr/bin/env python

"""
http://www.id3.org/id3v2-00
http://www.id3.org/id3v2.3.0
"""

import sys
import struct

def main():
    args = sys.argv[1:]
    if args:
        with open(args[0]) as f:
            input_string = f.read()
    else:
        input_string = sys.stdin.read()
    with Reader(input_string) as stream:
        assert stream.read(3) == "ID3"
        global version
        version = (stream.read_byte(), stream.read_byte())
        stream.flush("ID3v2." + ".".join(str(v) for v in version))

        flags = stream.read_byte()
        assert flags == 0
        stream.flush("flags")

        tag_size = stream.read_int28()
        stream.flush("tag_size: %i" % tag_size)

        with stream.sub_reader(tag_size) as tag_stream:
            read_tag(tag_stream)

        while stream.read_mp3_data() != None:
            stream.flush()

        # stream.allow_non_null_trail = True

def read_tag(stream):
    while True:
        if version[0] == 2:
            frame_id = stream.read(3)
            frame_size = stream.read_int24()
            frame_flags_string = ""
        else:
            frame_id = stream.read(4)
            frame_size = stream.read_int32()
            _frame_flags = stream.read_int16()
        if frame_id == "\x00" * len(frame_id):
            return
        stream.flush(repr(frame_id))

        with stream.sub_reader(frame_size) as tag_data_stream:
            read_tag_data(tag_data_stream)
def read_tag_data(stream):
    ISO_8859_1 = 0
    UTF16 = 1
    encoding = stream.read_byte()
    if encoding == ISO_8859_1:
        string = stream.read_null_terminated_iso_8859_1()
    elif encoding == UTF16:
        string = stream.read_utf16_with_bom()
    else:
        assert False
    stream.flush(repr(string))
    stream.allow_non_null_trail = True

class Reader:
    def __init__(self, input_string):
        self.string = input_string
        self.output_file = sys.stdout
        self.read_index = 0
        self.write_index = 0
        self.indentation = ""
        self.current_sub_reader = None
        self.allow_non_null_trail = False
    def read(self, length):
        if self.current_sub_reader != None:
            assert self.current_sub_reader.write_index == len(self.current_sub_reader.string)
            self.current_sub_reader = None
        result = self.string[self.read_index : self.read_index + length]
        assert len(result) == length
        self.read_index += length
        return result
    def read_byte(self):
        return ord(self.read(1))
    def read_int16(self):
        return struct.unpack(">H", self.read(2))[0]
    def read_int24(self):
        return (
            self.read_byte() << 16 |
            self.read_byte() << 8  |
            self.read_byte()
        )
    def read_int28(self):
        return (
            self.read_byte() << 21 |
            self.read_byte() << 14 |
            self.read_byte() << 7  |
            self.read_byte()
        )
    def read_int32(self):
        return struct.unpack(">I", self.read(4))[0]

    def read_null_terminated_iso_8859_1(self):
        result = []
        while True:
            c = self.read(1)
            if c == "\x00":
                return "".join(result)
            result.append(c)
    def read_mp3_data(self):
        if self.read_index == len(self.string):
            # don't crash on eof
            return None
        sync_word = "\xff\xfb"
        assert self.read(len(sync_word)) == sync_word
        start_index = self.read_index
        next_sync_word_index = self.string.find(sync_word, start_index)
        if next_sync_word_index == -1:
            next_sync_word_index = len(self.string)
        return self.read(next_sync_word_index - start_index)


    def flush(self, comment=None):
        if comment:
            self.output_file.write(self.indentation + "; " + comment + "\n")
        binary_string = " ".join(hex(ord(b))[2:].zfill(2) for b in self.string[self.write_index:self.read_index])
        self.write_index = self.read_index
        if binary_string:
            self.output_file.write(self.indentation + binary_string + "\n")
    def sub_reader(self, length):
        self.current_sub_reader = Reader(self.read(length))
        self.write_index = self.read_index
        self.current_sub_reader.indentation = self.indentation + "  "
        return self.current_sub_reader
    def __enter__(self):
        return self
    def __exit__(self, *args):
        if args[0]:
            return
        remainder = self.read(len(self.string) - self.read_index)
        if not remainder:
            return
        comment = None
        if not self.allow_non_null_trail:
            assert remainder == "\x00" * len(remainder)
            comment = "padding"
        self.flush(comment)

if __name__ == "__main__":
    main()

