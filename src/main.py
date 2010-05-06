
from pixel.xmlelement import XmlElement, element, collection, attribute
import pixel.parser

class Header(XmlElement):
    key = attribute(str)
    value = attribute(str)
    
class Body(XmlElement):
    title = element(str, True) #optional element
    text = element(str)
    
class Message(XmlElement):
    source = attribute(str)
    destination = attribute(str)
    id = attribute(int, True) #optional attribute.
    headers = collection(Header)
    body = element(Body)
    
    def send(self):
        print "Sendig message to %s" % self.destination
        
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
    
    message.headers.append(header1)
    message.headers.append(header2)
    
    xml = str(message)
    print "--- The orignial message object xml ---"
    print xml
    #load message from xml
    
    reader = pixel.parser.XmlReader(Message)
    loaded_message = reader.parse(xml)
    
    print "--- The loaded message object xml ---"
    print str(loaded_message)
    
    print "--- doing some actions ---"
    loaded_message.send()
    

if __name__ == "__main__":
    main()
