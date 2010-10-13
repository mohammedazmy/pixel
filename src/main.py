
from pixel.xmlelement import XmlElement, XmlListElement, element, collection, attribute, innertext
import pixel.loader
    
class Header(XmlElement):
    __ns__ = "http://www.thebetechnology.com/message"
    key = attribute(str)
    value = innertext(str)
    
class Body(XmlElement):
    __ns__ = "http://www.thebetechnology.com/message"
    title = element(str, True) #optional element
    text = element(str)
    
class Message(XmlElement):
    __ns__ = "http://www.thebetechnology.com/message"
    source = attribute(str)
    destination = attribute(str)
    id = attribute(int, True) #optional attribute.
    headers = collection(Header, optional=True)
    body = element(Body)
    status = attribute(str)
    
    def __init__(self):
        super(Message, self).__init__(self)
        
        self.status = "UNREAD"
        
    def send(self):
        print "Sendig message to %s" % self.destination

class Inbox(XmlListElement):
    name = attribute(str)
    __type__ = Message
    
    
def main():
    inbox = Inbox()
    inbox.name = "Test name"
    message = Message()
    inbox.append(message)
    inbox.append(Message())
    message.source = 'source@mail.com'
    message.destination = 'destination@mail.com'
    message.id = 100
    message.body.text = 'Message body goes here'
    message.body.title = 'Message title'
    
    header1 = Header()
    header1.key = 'server-ip'
    header1.value = '127.0.0.1'
    
    header2 = Header()
    header2.key = 'priority'
    header2.value = 'HIGH'

    message.headers.append(header1)
    message.headers.append(header2)
    
    xml = str(inbox)
    print "--- The orignial message object xml ---"
    print xml
    #load message from xml
    
    loader = pixel.loader.PixelLoader(Inbox)
    loaded_inbox = loader.loadString(xml)
    
    print "--- The loaded message object xml ---"
    print str(loaded_inbox)
    
    for m in loaded_inbox:
        print "Message:-------"
        m.status = 'READ'
        print m
        
    #print "--- doing some actions ---"
    #loaded_.send()
    

if __name__ == "__main__":
    main()
