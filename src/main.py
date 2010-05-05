
from xml import sax
from pixel.xmlelement import XmlElement, element, collection, attribute

class Header(XmlElement):
    key = attribute(str)
    value = attribute(str)
    
class Body(XmlElement):
    title = element(str)
    text = element(str)
    
class Message(XmlElement):
    source = attribute(str)
    destination = attribute(str)
    id = attribute(int)
    headers = collection(Header)
    body = element(Body)
    
def main():
    pass
    

if __name__ == "__main__":
    main()
