#!/usr/bin/env python

import sys

readable = ("" +
  "................................" +
  " !\"#$%&'()*+,-./0123456789:;<=>?" +
  "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_" +
  "`abcdefghijklmnopqrstuvwxyz{|}~." +
  "................................" +
  "................................" +
  "................................" +
  "................................" +
"")

def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--dump", action="store_true")
  parser.add_argument("-w", "--width", type=int, default=16)
  parser.add_argument("input", nargs="?", default="-")
  parser.add_argument("chunks", nargs="*")
  parser.add_argument("-o", "--output", default="-")
  args = parser.parse_args()
  chunk_descriptions = []
  for chunk_str in args.chunks:
    try:
      index = chunk_str.index(":")
    except ValueError:
      chunk_descriptions.append((int(chunk_str), None))
    else:
      chunk_descriptions.append((int(chunk_str[:index]), chunk_str[index + 1:]))
  chunk_descriptions.reverse()

  with open_read_path(args.input) as input:
    with open_write_path(args.output) as output:
      if args.dump:
        while True:
          try:
            width, comment = chunk_descriptions.pop()
          except IndexError:
            width = args.width
            comment = None
          if width == 0:
            if comment != None:
              output.write("; " + comment + "\n")
            else:
              output.write("\n")
            continue
          chunk = input.read(width)
          if chunk == "":
            break
          line = " ".join(hex(ord(x))[2:].zfill(2) for x in chunk)
          if comment == None:
            comment = "".join(readable[ord(c)] for c in chunk)
          if comment != "":
            line = line.ljust(width * 3 - 1) + "  ; " + comment
          output.write(line + "\n")
      else:
        for line in input.readlines():
          comment_index = line.find(";")
          if comment_index != -1:
            line = line[:comment_index]
          line = line.rstrip().replace(" ", "")
          output.write("".join(chr(int("".join(b), 16)) for b in zip(*[iter(line)]*2)))

def open_read_path(path):
  if path == "-":
    return DontTouchIt(sys.stdin)
  return open(path, "r")
def open_write_path(path):
  if path == "-":
    return DontTouchIt(sys.stdout)
  return open(path, "w")
class DontTouchIt(object):
  def __init__(self, arg):
    self.arg = arg
  def __enter__(self):
    return self.arg
  def __exit__(self, *args):
    pass

if __name__ == "__main__":
  main()
