import argparse
import sys
from .comparator import ComparatorEngine

def main():
    parser = argparse.ArgumentParser(prog="schema-compare")
    subparsers = parser.add_subparsers(dest="command", required=True)

    up = subparsers.add_parser("upload", help="Index a new schema")
    up.add_argument("file")
    up.add_argument("--name")

    args = parser.parse_args()
    engine = ComparatorEngine()

    if args.command == "upload":
        sid = engine.process_and_upload(args.file, args.name)
        if sid: print(f"Successfully indexed: {sid}")
        else: sys.exit(1)

if __name__ == "__main__":
    main()