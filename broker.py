#!/usr/bin/python3

import threading
import socket
import sys
import time
import os
import re
import getopt
import select

'''' The following multiline comments that are quoted into special quotation marks provide 
analytical explanation on some global variables that are defined right before the execution 
of main function. I will explain them here since they are used a lot in the functions of the
program, hence it would be better to define their use before seen written in code
'''

'''sub_con_adr is a list of lists that stores all the subscirbers
that have connected to the broker in the form of a list [conn,addr]. It is constantly updated 
in a sub thread meaning that if a connection is lost (e.g the subscriber suddenly terminates 
his program) the list will erase his entity. '''

'''pub_con_adr is a list of lists that stores all the publishers
that have connected to the broker in the form of a list [conn,addr]. It is constantly updated 
in a sub thread meaning that if a connection is lost (e.g the publisher suddenly terminates his
 program) the list will erase his entity'''

''' subscriptions is a dictionary that stores all the subscriptions of the subscribers 
in a key - value form. Key is the topic which starts with a hashtag and value is a list of lists 
with all the subscribers. For each subscriber we store his sub id and the socket that connects the broker
with the specific subscriber. For example subscriptions may look like:

{'#hello': [], '#world': [['s01', <socket.socket fd=548, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9090), raddr=('127.0.0.1', 40001)>], 
['s01', <socket.socket fd=352, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9090), raddr=('127.0.0.1', 43000)>]], 
'#great': [['s01', <socket.socket fd=548, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9090), raddr=('127.0.0.1', 40001)>], 
['s01', <socket.socket fd=352, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9090), raddr=('127.0.0.1', 43000)>]]}

It is constantly updated meaning that if a subscriber unsubscribes from a topic he will be erased
from this dictionary. Moreover, if  a connection is lost (e.g the subscriber suddenly terminates his program)
all his subscriptions will be erased.
'''

'''The following variables:
P_PORT
S_PORT
 will be defined in the if __name__ == "__main__":
 loop at the end, depending on the sys.argv (system argument values)
 that the user has defined when he executed the current program
 '''

'''Variable HOST will not be provided as input to the program so we predefine it as 'localhost' before executing main function '''

#Function that makes mandatory to import all 2 first arguments (P_PORT, S_PORT) when calling the file to execute
def gethelp(argv): 
    arg_help = "-s <S_PORT> -p <P_PORT>"
    try:
        opts, args = getopt.getopt(argv[1:], "s:p:") 
    except:

        # Function that prints a message to help the user call the program properly - We will define it in a while...
        stop_wrong_import(arg_help) 
    if len (opts)!=2 : 
        stop_wrong_import(arg_help)
    else:
        pass

def stop_wrong_import(message): 
    print ('Please it is mandatory to import all the following arguments:')
    print(message)
    print ('The 2 mandatory arguments may be inserted at a random order')
    sys.exit(1)

def send_to_subs(topic_pub,message):
    message_to_subs='Received msg for topic '+topic_pub+': '+ message+'\n'
    for topic,subscribers in subscriptions.items():
        if topic==topic_pub:
            for subscriber in subscribers:
                connecting=subscriber[1]
                connecting.sendall(bytes(message_to_subs, "utf-8"))  

def receive_pubs():

    #We want the broker to constantly hear each publisher that uses this function 
    while True: 
        try:

            #pub_con_adr is a global list which is updated every time a new publisher connects.
            #But since this function will be executed in a daemon thread immediately after the broker.py starts,
            #we want at least one publisher to be connected in order to start checking for received messages
            if len(pub_con_adr)>0: 

                #In every iteration of this while loop, each publisher stored in pub_con_adr will have, 
                #for a very very short time interval, his socket checked in case he publishes something new.
                for publisher in pub_con_adr:

                    #Connex and address are obtained based on the way they are stored in pub_con_adr
                    connex=publisher[0]
                    address=publisher[1] 

                    #This is how we implement the timeout for each publisher. So each publisher stored in the
                    #pub_con_adr list will have only 0.0000001 sec before broker releases this socket and starts 
                    #waiting for messages from the next publisher stored in the list. In that way, in just one socket
                    # the broker can rotate all the publishers that have established a connection with him and 
                    # check them in a very short time period. Do not forget that this list is constantly updated in
                    #  real time in another sub-thread of this program so each time when the whole  list is iterated, 
                    # a renewed list will be checked again from scratch
                    on_time = select.select([connex], [], [], 0.0000001) 
                    if on_time[0]:
                        data = connex.recv(1024).strip()
                        data=data.decode()
                        data=str(data)

                        # We implement this if statement because after the socket.sendall() of the data in case an 
                        # empty string is received after a closed socket to just pass without checking
                        if data: 

                            #We will perform two stages of formalization checking. We want to be sure that the user 
                            #sends its messages under the correct formalization for example: 4 pub #world at_least_one_letter 
                            if (bool(re.search("^p\d+ pub ", data)))  and ' #' in data:
                                data=data.split()
                                Pub_Id=data[0]
                                if len(data)>3 and len(data[2])>1 and data[2][0]=='#': 
                                    topic=data[2]
                                    message_pub=" ".join(data[3:])
                                    back_to_pub='Published msg for topic '+topic+': '+ message_pub+'\n'
                                    print ('\n'+back_to_pub)
                                    connex.sendall(bytes(back_to_pub, "utf-8"))    
                                    send_to_subs(topic,message_pub)
                                else:
                                    print ('\n'+Pub_Id+' did not formalize his message. No publishment')
                                    connex.sendall(bytes("\nYou did not publish because you did not formalize your message", "utf-8")) 
                            else:

                                #We implement another formalization checking. This is just for a more thorough printing  because we wont perform any 
                                #publishment, but still if we know the Pub_Id we may print a more detailed message to the Broker terminal.
                                if (bool(re.search("^p\d+", data))) : 
                                    data=data.split()
                                    Pub_Id=data[0]
                                    print ('\n'+Pub_Id+' did not send a message with the correct formalization. Nothing is done')
                                
                                else:
                                    #Moreover with this checking, we can inform the publisher that maybe he did not initialize the id argument in a formalized way
                                    # when he firstly executed the program, and he needs to restart it
                                    connex.sendall(bytes('''We have received a wrong pub id. Maybe it was a fault of initilization of arguments 
                                    when you initiated the program. Check this out, and if so, restart the program.
                                    You did not insert a message with the correct formalization. Nothing was subscriber/unsubscribed\n''', "utf-8"))
                                    print ('\Publisher did not send a message with the correct formalization. Wrong Pub_id, maybe in the pub.py input argument. Nothing is done')
                                connex.sendall(bytes("You did not insert a message with the correct formalization. Nothing was done", "utf-8"))
                    
                    #This else is for the if on_time[0] loop meaning that we had a timeout 
                    else: 
                        pass

        # in case the publisher forces his exit by shutting down his program 
        #(by closing completely his command window) or by just quiting publishing and does not leave the dialogue with his pub program open            
        except ConnectionResetError: 
            print ('\nThe publisher connected in the socket:',address,' forced his exit by shutting down his program. \nWaiting for another (or the same) publisher to show up\n ')
            
            # We will also delete his existence in the sub_con_adr list since he is no longer connected!
            index_to_del=[publisher[1] for publisher in pub_con_adr].index(address)
            del pub_con_adr[index_to_del]
            pass 

# thread for publisher
def pubthread():

    # set up for publisher
    pub_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pub_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    pub_sock.bind((HOST, P_PORT))
    pub_sock.listen(10)
    print("\nBroker listening Pubs on %s %d \n" %(HOST, S_PORT))
    while True:

        #After the execution of a pub.py program (with the correct hearing port of the broker for pubs) in a terminal,
        # these conn,addr variables store the socket and the address of the established connection between the publisher
        # and the broker terminal. These variables will change if a new publisher  connects the proper way
        # from another terminal, using a different port of the localhost. 
        conn, addr = pub_sock.accept()

        #  So each time a new publisher connects, we have to store this values to the pub_con_addr list so that these credentials won't be
        #  lost for further use from broker.py, but only if there are less than 5 publishers connected at that moment. We could skip this
        #  regulation, but this exercise indicates that the architecture of the pub/sub system must be set to allow a maximum number 
        # of 5 publishers.  
        if len(pub_con_adr) <5:

            #setting each socket that will be further used for communication between server - publisher 
            #to zero (0) (non-blocking) mode to guarantee that recv() will never block indefinitely when we will 
            # call it in the next thread
            conn.setblocking(0) 

            #Finally conn,addr are stored in pub_con_adr list. Since a connection is established these values will be stored in
            #this list. After the termination of this connection (e.g if this publisher forces his exit by shuting down his terminal - program),
            # this list will be renewed and the credential of this connection will be erased. (this will happen in the daemon thread of
            # the function receive_pubs)
            pub_con_adr.append([conn,addr]) 
            print("\nA Publisher is Connected. Socket: " + addr[0] + ":" + str(addr[1]))
        else: 
            print("\nA Publisher tried to connect from Socket: " + addr[0] + ":" + str(addr[1])+'. System has reached capacity of 5 publishers so this publisher was not connected\n')
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()

def receive_subs():

    # We want the broker to constantly hear  each subscriber that uses this function
    while True: 
        try:

            #sub_con_adr is a global list which is updated every time a new subscriber connects.
            #But since this function will be executed in a daemon thread immediately after the broker.py starts,
            #we want at least one subscriber to be connected in order to start checking for received messages
            if len(sub_con_adr)>0: 

                #In every iteration of this while loop, each subscriber stored in sub_con_adr will have, 
                #for a very very short time interval, his socket checked in case he sends something new. 
                for subscriber in sub_con_adr:

                    #Connex and address are obtained based on the way they are stored in sub_con_adr
                    connex=subscriber[0]
                    address=subscriber[1] 
                    
                    #This is how we implement the timeout for each subscriber. So each subscriber stored in the
                    #sub_con_adr list will have only 0.0000001 sec before broker releases this socket and starts 
                    #waiting for messages from the next subscriber stored in the list. In that way, in just one socket
                    # the broker can rotate all the subscribers that have established a connection with him and 
                    # check them in a very short time period. Do not forget that this list
                    #is updated in real time in another sub-thread of this program so each time when the whole 
                    #list is iterated, a renewed list will be checked again from scratch
                    on_time = select.select([connex], [], [], 0.0000001)  
                    if on_time[0]: 
                        data = connex.recv(1024).strip()
                        data=data.decode()
                        data=str(data)

                        # We implement this if statement because after the socket.sendall() of the data in case an 
                        # empty string is received after a closed socket to just pass without checking
                        if data:

                            #We will perform two stages of formalization checking. We want to be sure that the user 
                            #sends its messages under the correct formalization for example: 3 unsub #world 
                            if (bool(re.search("^s\d+ sub ", data)) or bool(re.search("^s\d+ unsub ", data)))  and ' #' in data:
                                data=data.split()
                                Sub_Id=data[0] 
                                if data[1]=='sub':
                                    if len(data)==3 and len(data[2])>1 and data[2][0]=='#':

                                        #This if statement checks if there is definetely one subscriber subscribed in this topic 
                                        # or at least there had been one subscriber some time before unsubscribing 
                                        if data[2] in subscriptions: 
                                            subscribed=False
                                            for subscriber in subscriptions[data[2]]:
                                                
                                                #Now we check if the subscriber is already subscribed in this topic so we do not do anything
                                                # We check with the subscriber[1] which is the port in the localhost of the subscriber, 
                                                # because subscriber[0] which is the sub id may be false given twice. But the port never 
                                                # lies and this is what shows the uniquness of each subscriber
                                                if subscriber[1]==connex: 
                                                    print ('\n'+Sub_Id+ ' already Subscribed in ' +data[2])
                                                    connex.sendall(bytes("You are already subscribed in "+data[2], "utf-8"))
                                                    subscribed=True
                                                    break
                                            if not subscribed: 
                                                subscriptions[data[2]].append([Sub_Id,connex])
                                                print ('\n'+Sub_Id+ ' subscribed  in  ' +data[2])
                                                connex.sendall(bytes("Ok you subscribed in "+data[2], "utf-8"))
                                        
                                        #Noone has ever subscribed in this topic, we have to initiate the subscription
                                        else :
                                            subscriptions[data[2]]=[[Sub_Id,connex]]
                                            print ('\n'+Sub_Id+ ' subscribed  in  ' +data[2])
                                            connex.sendall(bytes("Ok you subscribed in "+data[2], "utf-8"))
                                    else:
                                        print ('\n'+Sub_Id+' did not formalize his message. No subscription/unsubscription')
                                        connex.sendall(bytes("\nYou did not subscribe because you did not formalize your message", "utf-8"))
                                elif data[1]=='unsub': 
                                    
                                    #this try/except is for KeyError in case the subscriber tries to unsubscribe from a topic he is not subscribed
                                    try:

                                        # Once again, we want to make sure that the formalization was  followed by the subscriber before we unsubscribe him
                                        if len(data)==3 and len(data[2])>1 and data[2][0]=='#': 
                                            for subscriber in subscriptions[data[2]]:

                                                #Checking if the subscriber is already subscribed in this topic and we can unsubscribe him
                                                if subscriber[1]==connex: 
                                                    subscriptions[data[2]].remove(subscriber)
                                                    print ('\n'+Sub_Id+ ' Unsubscribed by ' +data[2])
                                                    connex.sendall(bytes("You unsubscribed from "+data[2], "utf-8"))  
                                                    break
                                        else:
                                            print ('\n'+Sub_Id+' did not formalize his message. No subscription/unsubscription')
                                            connex.sendall(bytes("\nYou did not unsubscribe because you did not formalize your message", "utf-8"))
                                    except KeyError:
                                        print ('\n'+Sub_Id+' tried to unsubcribe from topic'+data[2]+ ' that he is not subscribed')
                                        connex.sendall(bytes("\nYou are not subscribed in "+data[2]+' so you can not unsubscribe from that topic', "utf-8"))
                            else:

                                #We implement another formalization checking. This is just for a more thorough printing  because we wont perform any subscription/
                                #unsubscription, but still if we know the Sub_Id we may print a more detailed message to the broker terminal.
                                if bool(re.search("^s\d+", data)): 
                                    data=data.split()
                                    Sub_Id=data[0]
                                    print ('\n'+Sub_Id+' did not send a message with the correct formalization. Nothing is done')
                                else:

                                    #Moreover with this checking, we can inform the subscriber that maybe he did not initialize the id argument in a formalized way
                                    # when he firstly executed the program, and he needs to restart it
                                    connex.sendall(bytes('''We have received a wrong sub id. Maybe it was a fault of initilization of arguments 
                                    when you initiated the program. Check this out, and if so, restart the program.
                                    You did not insert a message with the correct formalization. Nothing was subscribed/unsubscribed\n''', "utf-8"))
                                    print ('\nSubscriber did not send a message with the correct formalization. Wrong Sub_id, maybe in the sub.py input argument. Nothing is done')
                                connex.sendall(bytes("You did not insert a message with the correct formalization. Nothing was done", "utf-8"))
                    
                    #This else is for the if on_time[0] loop meaning that we had a timeout
                    else:  
                        pass
        
        # in case the subscriber forces his exit by shutting down his program 
        #(by closing completely his command window) or by just quiting subscribing and does not leave the dialogue with his sub program open
        except ConnectionResetError: 
            print ('\nThe subscriber connected in the socket:',address,' forced his exit by shutting down his program. \nWaiting for another (or the same) subscriber to show up\n ')
            
            # We will also delete his existence in the sub_con_adr list since he is no longer connected!
            index_to_del=[subscriber[1] for subscriber in sub_con_adr].index(address)
            del sub_con_adr[index_to_del]

            #We will also delete all his subscriptions since he is no longer connected!
            for val in subscriptions.values():
                if connex in [subb[1] for subb in val]:
                    index_to_del=[subb[1] for subb in val].index(connex)
                    del val[index_to_del]
            pass

# thread for subscriber
def subthread():

    # set up for subscriber
    sub_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sub_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sub_sock.bind((HOST, S_PORT))
    sub_sock.listen(10)
    print("\nBroker listening Subs on %s %d \n" %(HOST, S_PORT))
    while True:

        #After the execution of a sub.py program (with the correct hearing port of the broker for subs) in a terminal,
        # these conn,addr variables store the socket and the address of the established connection between the subscriber
        # and the broker terminal. These variables will change if a new subscriber  connects the proper way
        # from another terminal, using a different port of the localhost. 
        conn, addr = sub_sock.accept()

        #  So each time a new subscriber connects, we have to store this values to the sub_con_addr list so that these credentials won't be
        #  lost for further use from broker.py, if and only if there are less than 5 subscribers connected at that moment. We could skip this
        #  regulation, but this exercise indicates that the architecture of the pub/sub system must be set to allow a maximum number 
        # of 5 subscribers. 
        if len(sub_con_adr) <5:


            #setting each socket that will be further used for communication between server - subscriber 
            #to zero (0) (non-blocking) mode to guarantee that recv() will never block indefinitely when 
            # we will call it in the next thread
            conn.setblocking(0) 

            #Finally conn,addr are stored in sub_con_adr list. Since a connection is established these values will be stored in
            #this list. After the termination of this connection (e.g if this subscriber forces his exit by shuting down his terminal - program),
            # this list will be renewed and the credential of this connection will be erased. (this will happen in the daemon thread of
            # the function receive_subs)
            sub_con_adr.append([conn,addr]) 
            print("\nA Subscriber is Connected. Socket: " + addr[0] + ":" + str(addr[1]))
        else: 
            print("\nA Subscriber tried to connect from Socket: " + addr[0] + ":" + str(addr[1])+'. System has reached capacity of 5 subscribers so this subscriber was not connected\n')
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()

# Function that receives another function and executes it as a daemnon thread
def start_thread_daemon(thread_func):
    thread=threading.Thread(target=thread_func,daemon=True)
    thread.start()

def main():
    start_thread_daemon(pubthread)
    start_thread_daemon(subthread)
    start_thread_daemon(receive_subs) 
    start_thread_daemon(receive_pubs) 

    # Pause for a while in order to wait for the pub/sub thread to print the port they are listening before giving instructions 
    #how to kill the program
    time.sleep(1) 
    print ('Both threads of the publisher and the subscriber are running as Daemon Threads. Press any key to kill the main thread and kill them as well ')
    print ('\n')
    os.system("pause")
    print ("\nBye - Bye, Hope to see you again\n")
    
if __name__ == "__main__":

     # We want to make sure that we will receive all the necessary arguments when executing the program
    gethelp(sys.argv)
    
    #reading the arguments from the execution of the .py file
    for i in range (len(sys.argv)): 

        #The ports must be integers not strings!
        if sys.argv[i]=='-s': 
            S_PORT=int(sys.argv[i+1])
        if sys.argv[i]=='-p': 
            P_PORT= int(sys.argv[i+1])
    
    # We won't implement a try except keyboard interrupt. Since our main is composed of 4 daemon threads and then we have os.system("pause")
    # at the very end of main, The user can stop the program by pressing any key which will terminate os.system("pause") and then finish the 
    # program
    HOST = "localhost" 
    sub_con_adr=[]
    pub_con_adr=[]
    subscriptions={}
    main()
