import argparse
import sys
from chain import IGoWChain
from demo import run_demo


def main(argv=None):
    """Simple CLI for common IGoW tasks: demo, save, load, snapshot."""
    parser = argparse.ArgumentParser(prog="igow", description="IGoW CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("demo", help="Run the interactive demo")

    save_p = sub.add_parser("save", help="Save current chain to <file>")
    save_p.add_argument("file", help="Path to save JSON")

    load_p = sub.add_parser("load", help="Load chain from <file>")
    load_p.add_argument("file", help="Path to load JSON")

    snap_p = sub.add_parser("snapshot", help="Create a snapshot of a new chain")

    args = parser.parse_args(argv)

    if args.cmd == "demo":
        run_demo()
    elif args.cmd == "save":
        # create a new chain for demo purposes and save it
        chain = IGoWChain()
        path = args.file
        chain.save_to_file(path)
        print(f"Saved chain to {path}")
    elif args.cmd == "load":
        chain = IGoWChain.load_from_file(args.file)
        print(f"Loaded chain with {len(chain.chain)} blocks")
    elif args.cmd == "snapshot":
        chain = IGoWChain()
        chain.add_block("Snapshot test")
        path = chain.save_snapshot()
        print(f"Saved snapshot: {path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
