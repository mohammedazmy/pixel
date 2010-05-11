
from pixel.xmlelement import XmlElement, element, collection, attribute
import pixel.loader
    
class Header(XmlElement):
    __ns__ = "http://www.thebetechnology.com/message"
    key = attribute(str)
    value = attribute(str)
    
class Body(XmlElement):
    __ns__ = "http://www.thebetechnology.com/message"
    title = element(str, True) #optional element
    text = element(str)
    
class Message(XmlElement):
    __ns__ = "http://www.thebetechnology.com/message"
    source = attribute(str)
    destination = attribute(str)
    id = attribute(int, True) #optional attribute.
    headers = collection(Header)
    body = element(Body)
    
    def send(self):
        print "Sendig message to %s" % self.destination

class ComplexHeader(Header):
    flags = collection(Header)
    
def main():
    message = Message()
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
    
    compHeader = ComplexHeader()
    compHeader.key = 'complex'
    compHeader.value = 'SUB-HEADER'
    compHeader.flags.append(header1)
    compHeader.flags.append(header2)
    
    message.headers.append(header1)
    message.headers.append(header2)
    message.headers.append(compHeader)
    
    xml = str(message)
    print "--- The orignial message object xml ---"
    print xml
    #load message from xml
    
    loader = pixel.loader.PixelLoader(Message)
    loaded_message = loader.loadString(xml)
    
    print "--- The loaded message object xml ---"
    print str(loaded_message)
    
    print "--- doing some actions ---"
    loaded_message.send()
    

if __name__ == "__main__":
    main()
