from optparse import OptionParser
import subprocess
import re
import time

def run_cmd(cmd):
    return subprocess.check_output(cmd.split(' ')).decode('utf-8').split("\n")

def test_port(ip, port):
    test_port_re = re.compile('^\s*%s\/\w+\s+open' % port)
    for line in run_cmd('nmap -p%s %s' % (port, ip)):
        if not test_port_re.search(line) is None:
            return True
    return False

parser = OptionParser()
parser.add_option("-i", "--ip", dest="ip",
                  help="IP address", metavar="IP")
parser.add_option("-p", "--port", dest="port",
                  help="Port", metavar="PORT")
parser.add_option("-c", "--count", dest="count",
                  help="Count", metavar="COUNT")

(options, args) = parser.parse_args()

if options.ip is None or options.port is None or options.count is None:
    raise RuntimeError("Must specify both -i for IP address and -p for port and -c for retry count!")

for i in range(0, int(options.count)):
    if test_port(options.ip, options.port):
        print('Port is up!')
        break;
    else:
        print('Not up!')
        time.sleep(1)
