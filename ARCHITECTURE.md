Docker containers management program
===================================
Goals
-----
The goals is to manage Docker containers on a single machine.

So implement program as a shell, which receives user commands.

User can be able to run, stop, start, remove containers.
Get list of Docker images and running containers.

Logs should have identifiable name: "container id + container name.log"

Design
------
In order to communicate with Docker manager will make requests(shell commands) to Docker,
get its answer, parse and make appropriate actions.

Manager will have two threads:
 * main thread will receive commands from user, make requests and manage(run, start, stop)
   containers.
 * second thread will continuosly iterate over existing containers, make requests to their
   real Docker logs, fetch data and save to file.

### Classes, functions, objects
Class Container:
   Holds data about one container: id, name, log filename, last log update time,
   and more (in future).

Class Docker_Manager:
   Tracks containers created under the manager. 
   (Actually, containers created outside manager also can be joined)
   Manages container's lifecycle by communicating with docker.

Function request():
   Wrapper that runs shell command and returns error code, strout, strerr.

Function log_update_thread_function():
   Function running in a thread. Gets log from Docker and appends to file.
   Each time only new log content is requested, using 'docker logs --since' option.

Function main():
   Main loop.
   Receives user commands, preparser and calls for appropriate action.

Thread lock:
   Syncronizes access to shared data between threads.

Fails and constrains
--------------------
 * I had to run container as a daemon in order not to take stdin/stdout.
 * Stop, start, rm commands can receive only one container id or name without options
   because it requires better command parsing.
 * Thread requests log from stopped containers. Container status track is needed.
 * Shell request are implemented in Docker_Manager class. Must be separated

Future
------
 1. Implement separate Parsing module(class), that will perform options check, splits.
    Handle requests where action on multiple containers can be specified (like stop/start/rm).

 2. Remove requests from Docker_Manager class and implement it as separate Request module(class),
    that will perform requests to shell(or different mechanism, eg. Python API).

 3. Keep track of containers that finished to run by themselves, or were stopped from outside.

 4. Implement history, autocomplete, etc for shell interface.

 5. In order to be able to deploy the manager to the cloud, implement client-server architecture.
    * Client can start new container and signal to the server. Server will collect logs.
    * Current implementation also can be parallelized, script can be run:
       - as one thread/process per container;
       - or thread/process that manages many containers;

 6. Live stats collection, resource management, inter-containers communication, can be also implemented
    on the basis of current architecture with addition of proper requests.


Bugs
----
 * Log filename "date + container name.log" would be better.
 
