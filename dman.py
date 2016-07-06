#!/usr/bin/env python
import subprocess
import threading
import time
import argparse
import os
from subprocess import PIPE

# thread lock
lock = None

# instance of Docker_Manager class
dman = None

# thread function to update logs for each container
def log_update_thread_func():
    while 1:
        lock.acquire()
        if len(dman.containers) == 0:
            break;
        for (key, cont) in dman.containers.items():
            dman.container_log_update(key)
        lock.release()
        time.sleep(1)

# function to run shell subprocess to get data from Docker
def request(req):
    proc = subprocess.Popen(req, shell = True, stdout = PIPE, stderr = PIPE)
    (out, err) = proc.communicate()
    proc.wait()
    ret = proc.returncode
    return (ret, out, err)

"""
class Container holds data about each started container
For the future:
    - add setters/getters
    - add other fields to store status, statistics, resources, etc.
"""
class Container:
    def __init__(self, container_id, container_name):
        self.id = container_id
        self.name = container_name
        self.log_filename = self.name + '_' + self.id + '.log'
        self.last_log_time = None

"""
class Docker_Manager - keeps track and manages all flow.
"""
class Docker_Manager:
    # Class constructor
    def __init__(self, path):
        self.containers = {}
        self.name_id_map = {}
        self.log_dir = path

    # Function to add new container instance to manager
    def container_add(self, container_id):
        cont_id = container_id
        cont_name = None
        req = "docker ps --filter 'id={}' --format '{{{{.ID}}}} {{{{.Names}}}}'".format(container_id)
        (r, o, e) = request(req)
        if r == 0:
            tokens = o.split()
            cont_id = tokens[0]
            cont_name = tokens[1]

        c = Container(cont_id, cont_name)
        self.containers[cont_id] = c
        self.name_id_map[cont_name] = cont_id
        return cont_id

    # Get container by id or by name
    def container_get(self, cont_id_or_name):
        container_id = cont_id_or_name
        if cont_id_or_name in self.name_id_map:
            container_id = self.name_id_map[cont_id_or_name]

        if container_id in self.containers:
            return self.containers[container_id]

        return None

    # Stop container:
    #    make shell request to Docker and return result
    def container_stop(self, cont_id_or_name):
        c = self.container_get(cont_id_or_name)
        res = -1
        mes = ""
        if c:
            (res, o, e) = request("docker stop " + cont_id_or_name)
            if res == 0:
                o = o.strip('\n')
                mes = o
            else:
                mes = e
        else:
            mes = cont_id_or_name + ": container does not exist"

        return (res, mes)

    # Start container:
    #    make shell request to Docker and return result
    def container_start(self, cont_id_or_name):
        c = self.container_get(cont_id_or_name)
        res = -1
        mes = ""
        if c:
            (res, o, e) = request("docker start " + cont_id_or_name)
            if res == 0:
                o = o.strip('\n')
                mes = o
            else:
                mes = e
        else:
            mes = cont_id_or_name + ": container does not exist"

        return (res, mes)

    # Remove container:
    #    make shell request to Docker,
    #    handle container deletion and return result
    def container_rm(self, cont_id_or_name):
        c = self.container_get(cont_id_or_name)
        res = -1
        mes = ""
        if c:
            (res, o, e) = request("docker rm " + cont_id_or_name)
            if res == 0:
                o = o.strip('\n')
                mes = o
                del(self.name_id_map[c.name])
                del(self.containers[c.id])
            else:
                mes = e
        else:
            mes = cont_id_or_name + ": container does not exist"

        return (res, mes)

    # Get list of existing containers
    def containers_list_get(self):
        containers_list = set()
        for (k, v) in self.containers.items():
            containers_list.add((v.id, v.name))
        return containers_list

    # Update container log:
    #    make shell request to Docker to get log
    #    append data to file
    def container_log_update(self, cont_id_or_name):
        c = self.container_get(cont_id_or_name)
        if not c:
            return

        req = ""
        if not c.last_log_time:
           req = "docker logs -t {}".format(c.id)
        else:
           req = "docker logs -t --since='{}' {}".format(c.last_log_time, c.id)

        (r, o, e) = request(req)
        if r == 0:
            tokens = o.split('\n')
            if c.last_log_time:
                tokens.pop(0)
            tokens = filter(None, tokens)
            if len(tokens):
                c.last_log_time = tokens[-1].split()[0]
                f = open(os.path.join(self.log_dir, c.log_filename), 'a')
                f.write('\n'.join(tokens)+'\n')
                f.close()


    # Clean up function calles on exit:
    #     stop, update log for the las time, remove container.
    def clear(self):
        ll = self.containers_list_get()
        lock.acquire()
        for (c_id, c_name) in ll:
            (res, mes) = self.container_stop(c_id)
            print "Stopped: ", mes
            dman.container_log_update(c_id)
            (res, mes) = self.container_rm(c_id)
            print "Removed: ", mes
        del ll
        lock.release()


def main():

    # Handle 'log_file' command line argument for the script
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--log_file', default='.', help="Path to store log files")
    args = args_parser.parse_args()

    # Handle path
    path = os.path.realpath(args.log_file)
    if not os.path.exists(path):
        print "Path: '{}' does not exist".format(path)
        exit()
    if not os.path.isdir(path):
        path = os.path.dirname(path)

    global dman
    dman = Docker_Manager(path)

    log_thread = threading.Thread(target = log_update_thread_func)

    global lock
    lock = threading.Lock()

    print "Type 'help' for Help"

    # Main loop to handle user input
    # and do appropriate action
    while 1:
        user_input = raw_input("dman># ")
        tokens = user_input.split(' ', 1)
        if tokens[0] == "run":
            lock.acquire()
            (r, o, e) = request("docker run -d " + tokens[1])
            if r == 0:
                o = o.strip('\n')
                short_id = dman.container_add(o)
                print short_id
                if not log_thread.is_alive():
                    log_thread.start()
            else:
                print e
            lock.release()

        elif tokens[0] == "stop":
            if len(tokens) == 2:
                (res, mes) = dman.container_stop(tokens[1])
                print "Stopped: ", mes
            else:
                print "Usage: stop CONTAINER"

        elif tokens[0] == "start":
            if len(tokens) == 2:
                (res, mes) = dman.container_start(tokens[1])
                print mes
            else:
                print "Usage: start CONTAINER"

        elif tokens[0] == "rm":
            if len(tokens) == 2:
                (res, mes) = dman.container_rm(tokens[1])
                print "Removed: ", mes
            else:
                print "Usage: rm CONTAINER"

        elif tokens[0] == "images":
            (r, o, e) = request("docker images")
            if r == 0:
                print o

        elif tokens[0] == "list":
            ll = dman.containers_list_get()
            for (c_id, c_name) in ll:
                print c_id, c_name
            del ll

        elif tokens[0] == "help":
            s = "Usage:\n" \
                    "'images' - list Docker images\n" \
                    "'run [options] IMAGE [COMMAND]' - Docker container will be run as a daemon\n" \
                    "'list' - list containers\n" \
                    "'stop CONTAINER' - stop container\n" \
                    "'start CONTAINER' - start container\n" \
                    "'rm CONTAINER' - remove container\n" \
                    "'exit'"
            print s

        elif tokens[0] == "exit":
            dman.clear()
            if log_thread.is_alive():
                log_thread.join()
            print "Good bye."
            break;

        else:
            print "Command not supported"

if __name__ == "__main__":
   main()
