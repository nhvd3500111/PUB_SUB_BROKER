	These .py files are meant to establish an architecture with a broker and multiple (max 5) publishers and multiple (max 5) subscribers using sockets in Python. 
	The IP addresses of broker.py, sub.py and pub.py are implied to be that of the current machine those programs are running on ('localhost'). They should be executed in the same local machine, and the only thing the respective user will define will be the individual ports recquired for each case. More specifically:

	      1) First of all, execute broker.py file. The IP address of the broker is implied to be that of the current machine the 	broker.py is running on ("localhost"). It recquires 2 arguments as input ,
 		-s (mandatory): the port of the  localhost where the broker hears the subscribers 
		-p (mandatory): the port of the  localhost where the broker hears the publishers .
You may insert those arguments at any order of preference e.g. python ./broker.py -s 9090 -p 9000 or python ./broker.py  -p 	9000 -s 9090 is the same.
	 
	      2) After that you may execute either file of the publisher or subscriber you want, based on how you want to exploit the system. So if you execute a sub.py file you have to provide as input the following arguments:
		 -i  (mandatory): the id of the subscriber (e.g s1). Its first letter must be s, followed by one or more integers                      (e.g s01), or else there will be a problem with the communication with the broker 
		 -h (mandatory): the ip of the broker/host (in our system it is always localhost) 
	         -p (mandatory): the port of the localhost where the broker hears the subscribers (in our case it should be the same 		         input as that given as -s when broker.py was executed) 
		 -r (mandatory): the port of the localhost which the current instance of the sub.py will use to communicate with the 		          broker
		 -s (optional): an optional parameter that indicates that the user demands a help message to better understand what 			  would be the mandatory arguments 
		 -f (optional): an optional parameter that indicates the path of a file name where there are commands that the 		  		  subscriber will execute once started and connected to the broker, before giving control to the user from the 				  keyboard. Apparently, if the file is stored in the same location of the drive where sub.py is stored, just 		  	          the name and the extension of the file are enough as arguments (e.g. -f sub_coms.cmnd) 
You may insert those arguments at any order of preference e.g. python ./sub.py -i s01 -h localhost -p 9090 -r 40001 -f sub_coms.cmd or  python ./sub.py -i s01  -p 9090 -h localhost -r 40001 -f sub_coms.cmd is the same, but if you insert a command file, this must 	always be inserted as the last argument of the sequence. 
	
	       3) Likewise, the pub file has the following arguments:
		  -i (mandatory): the id of the publisher(e.g p3). Its first letter must be p, followed by one or more integers (e.g                     p17), or else there will be a problem with the communication with the broker 
		  -h (mandatory): the ip of the broker/host (in our system it is always localhost) 
	          -p (mandatory): the port of the localhost where the broker hears the publishers (in our case it should be the 		          same input as that given as -p when broker.py was executed) 
		  -r (mandatory): the port of the localhost which the current instance of the pub.py will use to communicate with the 		   broker			  
		  -s (optional): an optional parameter that indicates that the user demands a help message to better understand what 		          would be the mandatory arguments 
		  -f (optional): an optional parameter that indicates the path of a file name where there are commands that the 		           publisher will execute once started and connected to the broker, before giving control to the user from the 		   		   keyboard. Apparently, if the file is stored in the same location of the drive where pub.py is stored, just the 		           name and the extension of the file 	are enough as arguments (e.g. -f pub_coms.cmnd) 
You may insert those arguments at any order of preference e.g. python ./pub.py -i p01 -h localhost -p 9000 -r 50001 -f pub_coms.cmnd or  python ./pub.py -i p01  -p 9000 -h localhost -r 50001 -f pub_coms.cmnd, but if you insert a command file, this must 	always be inserted as the last argument of the sequence. 

Finally, since it is multi - pub/ sub system, you may execute as many pub.py , sub.py fles as you want. But keep in mind that only 5 of each will be accepted to connect to the broker. The rest will constantly receive an error message until another pub (sub) is disconnected leaving an empty spot. Of course, each time you have to specify the respective port (-r) that each subscriber/publisher will use in the localhost (different port each time)