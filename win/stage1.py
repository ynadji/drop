import sys
import time
import urllib2
from optparse import OptionParser

def stage2uri():
    """Returns the full URI to the stage2.py script."""
    # For now, this will just return tyr. Eventually, it'll use
    # the VMs IP address to determine the gateway to in turn determine
    # the path.
    return 'http://tyr.gtisc.gatech.edu/stage2.py'

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 2

    # Download and run stage2
    times = 0
    stage2path = 'stage2.py'
    while times < 10:
        try:
            with open(stage2path, 'w') as stage2:
                response = urllib2.urlopen(stage2uri())
                stage2.write(response.read())
                break
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            times += 1
            time.sleep(7)

    try:
        sys.path.append('.')
        import stage2
        stage2.main()
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        sys.stderr.write('stage2.py execution failed!')
        return 1

if __name__ == '__main__':
    sys.exit(main())
