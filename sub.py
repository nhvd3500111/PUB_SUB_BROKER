#!/usr/bin/python3

import socket
import sys
import getopt
import time
import threading

'''The following variables:
 PORT_SUB
 HOST
 PORT_BROK
 SUB_ID
 will be defined in the if __name__ == "__main__":
 loop at the end, depending on the sys.argv (system argument values)
 that the user has defined when he executed the current program.'''

'''This following string variable message_to_subscriber will  be the message that the operator of the 
    program - subscriber will look at if the commands of his .cmd file run out or if he does not import a .cmd file. 
    Moreover after importing a correct message that does no raise errors, this message will appear again on his screen
     until he quits subscribing/unsubscribibg'''

message_to_subscriber='''If you want to quit subscribing there are four ways:\n
    a) Type quit
    b) Give empty input
    c) Give an input that will not start with an integer and then space.
    d) Perform KeyboardInterrupt
    On any other case I will assume that you are trying to subscribe or unsubscribe  from a thread
    If you want to subscribe somewhere, this must be formed as follows:
    10 sub #world
    If you want to unsubscribe from somewhere, this must be formed as follows:
    300 unsub #hello
    The first column in the file represents the number of seconds that the subscriber should wait before executing that 
    command (in the above cases 10 or 300). This number should be greater or equal to 0. The second column represents the command to execute:
     this will always be sub or unsub for the subscriber. The third column represents the topic that the subscriber will subscribe/unsubsribe 
     to. All topics both for publisher and subscriber are one keyword. If you do not use this formalization, and you have not quit this program,
      you will not subscribe/unsubsribe from anywhere but you will be asked again to give something as input.
    '''

# Function that receives another function and executes it as a daemnon thread
def start_thread_daemon(thread_func):
    thread=threading.Thread(target=thread_func,daemon=True)
    thread.start()

#Mandatory import of all 4 first arguments (only - f optional) when calling the file to execute
def gethelp(argv):
    arg_help = "-i <id> -h <ip> -p <brok> -r <sub> -f <file.cmd (optional)>"
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

#takes a formalized command, performs the pause depending on the
#seconds that command include, and then returns the rest of the text as a string     
def execute_command(command):
    all_info=command.split()

    #the first element of the new list is the seconds we will have to wait
    time.sleep(int(all_info[0])) 

    #We add the Sub _Id to the data that the subscriber will transmit. For example, data 
    # will be formalized as follows:      s1 sub #hello or s2 unsub #world etc
    data=SUB_ID+' '+all_info[1]+' ' 
    data=data+' '.join(all_info[2:])
    return data

#Function that initiates  a socket.socket which binds the socket of the subscriber and 
#connects with the socket that the broker hears the subscribers 
def initiate_socket(): 
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # We want our specific subscriber to transmit from a specific socket 
    sock.bind((HOST,PORT_SUB)) 

    #Connect to the specific socket that the broker hears the subscribers
    sock.connect((HOST, PORT_BROK)) 
    

def send_subs_unsubs(text,waiting=False): #function that communicates with the broker actively by sending him the commands after processing them 
    # from the input that the subscriber has entered manually or automatically (by the -f file)
    global sock
    data=execute_command(text)
    sock.sendall(bytes(data +  "\n", "utf-8"))

    #This is an optional time sleeping so that the user of the program has time to read what he received from the broker, 
    # before he sees in the screen of the command line the whole message_to_subscriber. Mind that when this function will be executed for 
    # reading all the commands in the -f file, waiting time must not be activated since the message_to_subscriber is not printed and the 
    # subscriptions/ unsubcriptions are executed automatically depending on the commands. Moreover, in this sleeping time, the user can not
    #  subscribe or unsubscribe manually because the input will be executed after the sleeping. But since this function will be executed in 
    # a thread, if in the meanwhile a publisher sends something regarding a topic that this subscriber is enrolled, he will see the message 
    # in his screen. 
    if waiting:
        time.sleep(5) 

#Receives not only the publishments of the topics that the subscriber is enrolled but also
#the info from the broker regarding the situation of his subscription /unsubscription request every time he sends a request
def always_listening():
    global sock

    #just a silly initial message to the terminal of the subscriber 
    print ('''No matter what happens during the execution of this program, I am a daemon thread that
    ,in 2 seconds from now, will start listening to  the broker all the time and print what sends 
    back until the execution of the current program is terminated ''')
    while True:

        #This is for ConnectionAbortedError, meaning that the Broker shut us down because he has reached max capacity (5) for subscribers
        try:
            received = str(sock.recv(1024), "utf-8") 
            print(received)
        except ConnectionAbortedError:
            break

def main():
    initiate_socket()
    start_thread_daemon(always_listening)

    #2 seconds for the subscriber to read the first print message inside the function always_listening
    time.sleep(2) 
    inputs=read_cmd_file ()
    if inputs is None:
        print ('You did not give input file, proceeding to manually input your subscriptions!\n')
        pass
    else:
        for command in inputs:

            #Here we leave the default waiting=False because we don't want to pause the program. The messages from 
            #the broker will be clear to see since print (message_to_subscriber) won't be executed.
            send_subs_unsubs(command) 
    
     #In my localhost there was a little lag in the final receipt of the message from the broker, so we give 1 second notice
    # to the deamon thread (always listening) to deliver us the final message before the message_to_subscriber appears on the screen      
    time.sleep(1)  
    print (message_to_subscriber)
    text_to_sub=input()
    try:
        while text_to_sub!='quit':

            #Here we  implement waiting=True because we  want to pause the program. 
            #The messages from the broker wont be clear to see since print (message_to_subscriber) will be executed to give instructions.
            #to the user for manual input of the messages to be published
            send_subs_unsubs(text_to_sub,waiting=True)

            #In my localhost there was a little lag in the final receipt of the message from the broker, so we give 1 second notice
            # to the deamon thread (always listening) to deliver us the final message before the message_to_subscriber appears on the screen
            time.sleep(1) 
            print (message_to_subscriber)
            text_to_sub=input()     
    except ValueError:
        print ('You gave input that did not  start with an integer and then space. Quiting...')
        sys.exit(0)
    except IndexError:
        print ('You gave empty input. Quiting...')
        sys.exit(0)    

if __name__ == "__main__":

    # We want to be sure that we will receive all the necessary arguments when executing the program
    gethelp(sys.argv) 

    #reading the arguments from the execution of the .py file
    for i in range (len(sys.argv)): 
        if sys.argv[i]=='-r':
            PORT_SUB=int(sys.argv[i+1])
        if sys.argv[i]=='-h':
            HOST= sys.argv[i+1]
        if sys.argv[i]=='-p':
            PORT_BROK= int(sys.argv[i+1])
        if sys.argv[i]=='-i':
            SUB_ID=sys.argv[i+1]
    
    try:
        main()

    #This exception handles the overload of the system. If the broker has already five subscribers conected, we will exit gently. We have raised
    #this exception both here and in daemon thread of always_listening function, because it would raise that error in both parts, if the 
    # broker had closed the socket for that reason.
    except ConnectionAbortedError: 
        print('\nFull capacity of subscribers. Please try to connect in a while if a connected subscriber quits his connection')
        time.sleep(2)
        sys.exit(0)

    #This exception may only be executed at the time of the manual inputs of the publisher
    except KeyboardInterrupt: 
        print ('You performed KeyboardInterrupt. Quiting....')
        sys.exit(0)
