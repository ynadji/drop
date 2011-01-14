import sys
from optparse import OptionParser

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 2

    return 0

if __name__ == '__main__':
    sys.exit(main())
