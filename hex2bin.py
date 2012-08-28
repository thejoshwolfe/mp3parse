#!/usr/bin/env python

import sys

def main():
    for line in sys.stdin.readlines():
        comment_index = line.find(";")
        if comment_index != -1:
            line = line[:comment_index]
        line = line.rstrip().replace(" ", "")
        sys.stdout.write("".join(chr(int("".join(b), 16)) for b in zip(*[iter(line)]*2)))

if __name__ == "__main__":
    main()
