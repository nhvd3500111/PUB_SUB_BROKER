#!/usr/bin/python3

import socket
import sys
import getopt
import time
import threading

'''The following variables:
 PORT_PUB
 HOST
 PORT_BROK
 PUB_ID
 will be defined in the if __name__ == "__main__":
 loop at the end, depending on the sys.argv (system argument values)
 that the user has defined when he executed the current program'''

'''This following string variable message_to_publisher will  be the message that the operator of the 
    program - publisher will look at if the commands of his .cmd file run out or if he does not import a .cmd file. 
    Moreover after importing a correct message that does no raise errors, this message will appear again on his screen
     until he quits publishing'''

message_to_publisher='''If you want to quit publishing there are four ways:\n
    a) Type quit
    b) Give empty input
    c) Give an input that will not start with an integer and then space.
    d) Perform KeyboardInterrupt
    On any other case I will assume that you are trying to publish something
    If you want to publish something, this must be formed as follows:
    3 pub #hello This is the first message.
    The first column in the file represents the number of seconds that the publisher should wait after connecting in order to execute that 
    command (in the above case 3). This number should be greater or equal to 0. The second column represents the command to execute: this 
    will always be pub for the publisher. The third column represents the topic that the publisher will publish to. All topics both for
     publisher and subscriber are one keyword. If you do not publish something with this formalization, and you have not quit this program, the 
     text you typed will not be published but you will be asked again to give something as input. '''

# Function that receives another function and executes it as a daemnon thread
def start_thread_daemon(thread_func):
    thread=threading.Thread(target=thread_func,daemon=True)
    thread.start()

#Mandatory import of all 4 first arguments (only - f optional) when calling the file to execute
def gethelp(argv): 
    arg_help = "-i <id> -h <ip> -p <brok> -r <pub> -f <file.cmd (optional)>"
    try:

        # f without : because -f is optional
        opts, args = getopt.getopt(argv[1:], "si:h:p:r:f") 
    except:

        # Function that prints a message to help the user call the program properly - We will define it in a while...
        stop_wrong_import(arg_help) 
    
    # We certainly have given less than 4 arguments (or more than five which is also bad) as input so interrupt! ()
    if len (opts)!=4 and len (opts)!=5 : 
        stop_wrong_import(arg_help)
    elif len (opts)==4:
        for opt,val in opts:

            #Someone needs help, s was typed as argument 
            if 's' in opt: 
                stop_wrong_import (arg_help)
            if opt not in ['-i', '-h', '-p','-r']:
                stop_wrong_import(arg_help)
            else :
                if val =='-f':
                    stop_wrong_import(arg_help)
                else:
                    pass
    else:
        pass

def stop_wrong_import(message): 
    print ('Please it is mandatory to import all the following arguments:')
    print(message)
    print ('The 4 mandatory arguments may be inserted at a random order, but if you insert -f <file.cmd>, this must be the last argument to be typed ')
    sys.exit(1)

#read the cmd file if exists   
def read_cmd_file (): 
    try:

        #Here f is with :, so if it will raise an error it will be that -f had not an input or -f had as input a directory that does not exist
        opts, args = getopt.getopt(sys.argv[1:], "si:h:p:r:f:") 
        for opt,val in opts:
            if opt=='-f':
                f = open(val,"r")
                contents = f.read()
                f.close() 
                return contents.splitlines()
    except:
        print ('\nNo input file was given as -f or incorrect path was given after -f')                


def execute_command(command):
    all_info=command.split()

    #the first element of the new list is the seconds we will have to wait
    time.sleep(int(all_info[0])) 

    #We add the Pub _Id to the data that the publisher will transmit. For example, data will 
    # be formalized as follows:      p1 pub #hello Lalala  or p2 pub #world good morning
    data=PUB_ID+' '+all_info[1]+' '
    data=data+' '.join(all_info[2:])
    return data

#Function that initiates  a socket.socket which binds the socket of the publisher and 
#connects with the socket that the broker hears the publisher 
def initiate_socket(): 
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # We want our specific publisher to transmit from a specific socket 
    sock.bind((HOST,PORT_PUB)) 

    #Connect to the specific socket that the broker hears the publishers
    sock.connect((HOST, PORT_BROK)) 

#Function that sends the message to the broker, after taking it in the proper form by executing
#execute_command function in it. There is an optional boolean function called waiting. We will use 
#it when the program is entered in mode where the user has to enter his commands manually. This is because
#we want him to have a little time reading what the broker has returned from the previous message, before
# he sees the message_to_publisher in his screen (which is a pretty big one). After that, he will have the 
#chance to proceed to his next input
def execute_pub(text,waiting=False):
    global sock
    data=execute_command(text)
    sock.sendall(bytes(data +  "\n", "utf-8"))
    
    #As mentioned above this is an optional time sleeping so that the user of the program has time to read what he received from the broker, 
    # before he sees in the screen of the command line the whole message_to_publisher. Mind that when this function will be executed for 
    # reading all the commands in the -f file, waiting time must not be activated since the message_to_publisher is not printed and the 
    # publishments are executed automatically depending on the commands. Moreover, in this sleeping time, the user can not
    #  publish manually because the input will be executed after the sleeping.
    if waiting:
        time.sleep(5) 

#Receives he info from the broker regarding the situation of his publishments every time he publishes something
def always_listening():
    global sock

    #just a silly initial message to the terminal of the publisher
    print ('''No matter what happens during the execution of this program, I am a daemon thread that
    ,in 2 seconds from now, will start listening to  the broker all the time and print what sends 
    back until the execution of the current program is terminated ''')
    while True:

        #This is for ConnectionAbortedError, meaning that the Broker shut us down because he has reached max capacity (5) for publishers
        try:
            received = str(sock.recv(1024), "utf-8") 
            print(received)
        except ConnectionAbortedError:
            break




def main():
    initiate_socket()
    start_thread_daemon(always_listening)

    #2 seconds for the publisher to read the first print message inside the function always_listening
    time.sleep(2) 
    inputs=read_cmd_file ()
    if inputs is None:
        print ('You did not give input file, proceeding to manually input your publishments!\n')
        pass
    else:
        for command in inputs:

            #Here we leave the default waiting=False because we don't want to pause the program. The messages from 
            #the broker will be clear to see since print (message_to_publisher) won't be executed.
            execute_pub(command) 

    #In my localhost there was a little lag in the final receipt of the message from the broker, so we give 1 second notice
    # to the deamon thread (always listening) to deliver us the final message before the message_to_publisher appears on the screen
    time.sleep(1)          
    print (message_to_publisher)
    text_to_publish=input()
    try:
        while text_to_publish!='quit':

            #Here we   implement waiting=True because we  want to pause the program. 
            #The messages from the broker wont be clear to see since print (message_to_publisher) will be executed to give instructions.
            #to the user for manual input of the messages to be published
            execute_pub(text_to_publish,waiting=True)

            #In my laptop there was a little lag in the final receipt of the message from the broker, so we give 1 second notice
            # to the deamon thread (always listening) to deliver us the final message before the message_to_publisher appears on the screen
            time.sleep(1) 
            print (message_to_publisher)
            text_to_publish=input()     
    except ValueError:
        print ('You gave input that did not  start with an integer and then space. Quiting...')
        sys.exit(0)
    except IndexError:
        print ('You gave empty input. Quiting...')
        sys.exit(0)
    
if __name__ == "__main__":

    # We want to make sure that we will receive all the necessary arguments when executing the program
    gethelp(sys.argv) 

    #reading the arguments from the execution of the .py file
    for i in range (len(sys.argv)):
        if sys.argv[i]=='-r':
            PORT_PUB=int(sys.argv[i+1])
        if sys.argv[i]=='-h':
            HOST= sys.argv[i+1]
        if sys.argv[i]=='-p':
            PORT_BROK= int(sys.argv[i+1])
        if sys.argv[i]=='-i':
            PUB_ID=sys.argv[i+1]
    try:
        main()

    #This exception handles the overload of the system. If the broker has already five publishers conected, we will exit gently. We have raised
    #this exception both here and in daemon thread of always_listening function, because it would raise that error in both parts if the 
    # broker had closed the socket for that reason.
    except ConnectionAbortedError: 
        print('\nFull capacity of publishers. Please try to connect in a while if a connected publisher quits his connection')
        time.sleep(2)
        sys.exit(0)

    #This exception may only be executed at the time of the manual inputs of the publisher
    except KeyboardInterrupt: 
        print ('You performed KeyboardInterrupt. Quiting....')
        sys.exit(0)


