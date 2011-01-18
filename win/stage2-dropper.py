import sys
import os
import time
import urllib2
import stat
import net
from optparse import OptionParser

def binarypath():
    chunks = ['http://', net.gateway(), '/', net.vmnumber(), '/sample.exe']
    return ''.join(chunks)

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] input"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 2

    # Download and execute binary.
    print('hello from stage2!')
    times = 0
    uri = binarypath()
    exe = os.path.join('.', uri[uri.rfind('/') + 1:])

    # Download and run binary
    while times < 10:
        try:
            with open(exe, 'wb') as binary:
                response = urllib2.urlopen(uri)
                binary.write(response.read())
                break
        except Exception as e:
            sys.stderr.write('stage2: ' + str(e) + '\n')
            sys.stderr.write('uri: ' + uri + '\n')
            times += 1
            time.sleep(7)

    try:
        os.chmod(exe, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.system(exe)
    except Exception as e:
        sys.stderr.write('stage2: ' + str(e) + '\n')
        sys.stderr.write('Malware sample execution failed!')
        return 1

if __name__ == '__main__':
    sys.exit(main())
