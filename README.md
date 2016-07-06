Docker containers management program
====================================
This Docker manager is as a shell-like program
that manages Docker containers.  

SYNOPSIS
--------
dman.py [--help] [--log_file filename]

DESCRIPTION
-----------
Manager allows user to run, stop, start, remove Docker containers,
get Docker images and list of containers started with the manager.

Messages for STDOUT and STDIN are saved in log files at specified path
under 'container id + container name.log' name.

OPTIONS
-------
       --help
         Print usage message.

       --log-path=path
         Specify path where log files will be saved.
         Default is current directory.

INTERFACE
---------
After started, program promts for commands.

dman># 

Available commands:
  help
    Print usage message.  

  images
    Lists installed Docker images.
    
  run [options] IMAGE [command]
    Runs container as a daemon.
  
  list
     Lists id and name of running cotainers.
  
  stop CONTAINER
     Stops container by its id or name.
  
  start CONTAINER
     Starts container by its id or name.


  rm CONTAINER
     Removes container by its id or name.

  exit
     Closes and removes all cotainers which were started
     through current interface.
     Closes manager.
