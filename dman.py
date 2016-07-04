#!/usr/bin/env python
import subprocess
from subprocess import PIPE

def request(req):
    proc = subprocess.Popen(req, shell = True, stdout = PIPE, stderr = PIPE)
    (out, err) = proc.communicate()
    proc.wait()
    ret = proc.returncode
    return (ret, out, err)


def main():

    while 1:
        user_input = raw_input("some input:")
        if user_input == "exit":
            break;

        print user_input
        (r, o, e) = request("docker run -d ubuntu-ttt /usr/games/tttt")

        print "ret: ", r
        print "out: ", o
        print "err: ", e


if __name__ == "__main__":
   main()
