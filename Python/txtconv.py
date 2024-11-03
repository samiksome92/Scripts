#!/usr/bin/env python3

"""A script to convert a text file from one encoding to another.

Both input and output encodings can be specified. If input encoding is not specified best guess is used. In addition
one can specify line endings to use for the output file. If no specific line ending is provided, line endings are the
same as in input file.
"""

import argparse
import codecs
import os
import sys

import charset_normalizer


def main() -> None:
    """Main function for the script."""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("txt_file", help="Text file to process")
    parser.add_argument("-f", "--from", dest="from_", help="Source encoding to convert from")
    parser.add_argument("-t", "--to", help="Target encoding to convert to", default="UTF-8")
    parser.add_argument("-l", "--newline", help="Line ending to use", choices=["lf", "crlf", "cr"], default="")
    parser.add_argument("-o", "--out_file", help="Output file", default=None)
    parser.add_argument("--overwrite", help="Overwrite text file", action="store_true")
    args = parser.parse_args()

    # Check if encodings are valid.
    try:
        if args.from_ is not None:
            codecs.lookup(args.from_)
        codecs.lookup(args.to)
    except LookupError as error:
        print(f"ERROR: {error}.")
        sys.exit(1)

    # Detect encoding using charset_normalizer if source encoding is not provided.
    if args.from_ is None:
        with open(args.txt_file, "rb") as file_obj:
            args.from_ = charset_normalizer.detect(file_obj.read())["encoding"]
        print(f"Using {args.from_} as source encoding.")

    # Set output file.
    if args.overwrite:
        # Output file is same as input if --overwrite is specified.
        args.out_file = args.txt_file
    elif args.out_file is None:
        # Else if output file is not given, use <txt_file>_<from>_<to>.txt as output file.
        dirname, basename = os.path.split(args.txt_file)
        args.out_file = os.path.join(dirname, f"{os.path.splitext(basename)[0]}_{args.from_}_{args.to}.txt")

    # Set read and write newlines.
    read_nl = "" if args.newline == "" else None
    write_nl = args.newline.replace("lf", "\n").replace("cr", "\r")

    # Read file.
    with open(args.txt_file, "r", encoding=args.from_, newline=read_nl) as file_obj:
        try:
            text = file_obj.read()
        except UnicodeDecodeError:
            print(f"ERROR: Text file cannot be decoded using {args.from_}.")
            sys.exit(1)

    # Ensure output encoding can encode all characters.
    try:
        text.encode(args.to)
    except UnicodeEncodeError:
        print(f"ERROR: All source characters cannot be encoded using {args.to}.")
        sys.exit(1)

    # Write file.
    with open(args.out_file, "w", encoding=args.to, newline=write_nl) as file_obj:
        file_obj.write(text)


if __name__ == "__main__":
    main()
