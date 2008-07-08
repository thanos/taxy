"""
A Syntazo project

(c)1997,1998,1999,2000-2008 Thanos Vassilakis


"""

import stackless

class DeliveryAgent(object): 
    """ 
    Implements  a form of Visitor pattern.
    Its responsibility is to hold a message and deliver it to the 
    correct processor method of the current node.
        
    Use this class to encapsule a business message 
    and control what method processes it at a node.

    Was called Envelope - renamed to avoid confusion.
    """
    wayslip = None
    def __init__(self, wayslip=None, message=None):
        """     
        @param wayslip: this is by default None but can be used for routing information.
        @type wayslip: Wayslip object.
        @param message: message to be delivered
        @type message:  any object.
        """
        if wayslip: self.wayslip= wayslip
        self.message = message


    def processNode(self, node): 
        """ 
        invokes Node.processAgent 
        @param node: The node the message will be delivered to.
        @type node: Node object 
        @return: a message instance.
        """
        return node.processAgent(self)

        
class Node(object):
    """ 
    abstract node - don't use - always subclass 
    implentation of Node - with a single destination
    """
    destination = None
    name = ''
    def __init__(self, name=''):
        if name:
            self.name = name
        self.channel= stackless.channel()
        stackless.tasklet(self.run)() 



    def run(self):
        self.receive()

    def receive(self): 
        """ 
        if you override invoke the agent's 
        process method and pass result with send 
        """
        while 1:
            agent = self.channel.receive()
            if agent is None:
                break
            agent = agent.processNode(self)
            if agent:
                self.send(agent)

    def send(self, agent):  
        """ 
        Must be overridden.
        Should normally implement sending the agent onto the next node in the net work.
        override and always return self
        @param agent: the devilery agent
        @type   agent: DeliveryAgent
        @return: self
        """
        if self.destination:
            self.destination.send(agent)
        return self 

    def connect(self, receiver, *args): 
        """ 
        Must be overridden.
            - override and always return self
        @param receiver: the node to receive the processed message
        @type   receiver: Node subclass
        @param args: a list of args to facilitate the connection.
        @return: self
        """
        assert receiver, "receiver must not be None"
        self.destination = receiver.channel
        return self


    def disconnect(self, receiver=None, *args):
        """
        disconnects a node to this pipe.
        @param reciever: the node to be connected.
        @type receiver: node to be disconnected.
        @param *args: list of args to facilitate disconnection.

        @return: must return  self 
        @rtype: Node
        """
        self.destination = None
        return self

    def processAgent(self, agent): 
        """ 
        Override is you need access to the delivery agent

        @param agent: the delivery agent
        @type   agent: DeliveryAgent
        @return:  the delivery agent
        @rtype: DeliveryAgent
        """
        agent.message =  self.process(agent.message)
        return agent

    def process(self, message): 
        """ 
        Override to process message

        @param message: the sage to process
        @return:  the message
        """
        return message
        
class DbAgent(DeliveryAgent):
    def processNode(self, node):
        print self, '@', node
        return DeliveryAgent.processNode(self, node)

import sys, time
import stacklesssocket
class Url(Node):
        
    def run(self):
        oldSocket = sys.modules["socket"]
        sys.modules["socket"] = stacklesssocket
        import urllib  # must occur after monkey-patching!
        try:
            print 'before urlopen'
            
            f = urllib.urlopen(self.name, proxies = {'http': 'http://webproxy.ny.jpmorgan.com:8000'})
            if not isinstance(f.fp._sock, stacklesssocket.stacklesssocket):
                raise AssertionError("failed to apply monkeypatch")
            s = f.read()
            if len(s) != 0:
                print "Fetched", len(s), "bytes via replaced urllib"
            else:
                raise AssertionError("no text received?")
            self.send(DbAgent(message=s))
        finally:
            sys.modules["socket"] = oldSocket
            
            

if __name__ =='__main__':


 


    def simpleRouteTest(num):
        import time
        class CapsNode(Node):
            def process(self, message):
                return message[0].upper(), message[1], message[2]
        class Output(Node):
            total = 0
            count = 0
            def send(self, agent):
                t = time.time() - agent.message[2]
                self.total = self.total + t
                self.count = self.count +1
                if  agent.message[1] == num-1:
                    print '-->', agent.message, t
                    print self.total, self.count, self.total/self.count
                    

        class Sender(Node):
            def run(self):
                for i in xrange(num):
                    self.send(DbAgent(message =(self.name, i, time.time())))
    
        capsNode =CapsNode()
        capsNode.connect(Output())
        senders = [Sender(x) for x in "Hey boy! hello i'm just a bastard of hell".split()]
        for sender in senders:
            sender.connect(capsNode)

    def helloWorld():
        class Input(Node):
            def run(self):
                while 1:
                    name = raw_input("Enter your Name:")
                    if name =='quit': break
                    self.send(DbAgent(message =name))
        class Output(Node):
            def send(self, agent):
                print agent.message
        class Greeter(Node):
            def process(self, message):
                return "Hello " + message
        class ChitChat(Node):
            def process(self, message):
                return message+", so how are you?"
        Input().connect(Greeter().connect(ChitChat().connect(Output())))



    def ticker():
        class Poll(Url):
            def __init__(self, symbol):
                Url.__init__(self, 'http://quote.yahoo.com/d/quotes.csv?s=%s&f=sl1d1t1c1ohgvj1pp2owern&e=.csv'% symbol)
            def run(self):
                while 1:
                    Url.run(self)
                    secondsToWait = 3.0
                    endTime = time.time() + secondsToWait
                    while time.time() < endTime:
                        stackless.schedule()             
                
                      
        class Output(Node):
            def send(self, agent):
                print agent.message
                


        for symbol in 'ibm','sunw','mot':
            Poll(symbol).connect(Output())   
            
            
    

    #simpleRouteTest(10)
    #helloWorld()
    ticker()            
    stackless.run()

    
