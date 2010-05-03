
from xml import sax
from pixel.xmlelement import XmlElement, element, collection, attribute

class MyHandler(sax.ContentHandler):
    def __init__(self):
        sax.ContentHandler.__init__(self)
    
    def startElement(self, name, attrs):
        print "Start element %s" % name
        
        for attname, attvalue in attrs.items():
            print attname, ": ", attvalue
    
    def endElement(self, name):
        print "End element %s" % name
        
    def startDocument(self):
        print "Start Document"
    
    def endDocument(self):
        print "End Document"

    def characters(self, contents):
        print contents
        

class Info(XmlElement):
    name = element(str)
    age = element(int)

class Data(Info):
    address = element(str)
    location = element(Info)
    
class File(XmlElement):
    path = element(str)
    size = element(int)

class Package(XmlElement):
    name = attribute(str)
    domain = attribute(str)
    version = attribute(float)
    files = collection(File)
    
class Main(XmlElement):
    info = element(Info)
    data = element(Data)
    packages = collection(Package)
    

class Property(XmlElement):
    key = element(str)
    value = element(str)
    
def main():
    """ Test code """    
    sax.parseString(
"""
<main>
    <info>
        <name>Mohammed Azmy</name>
        <age>27</age>
    </info>
    <elements>
        <Element name='name' data='ag'>Azmy</Element>
        <Element name='age'/>
    </elements>
</main>""", MyHandler())
    

if __name__ == "__main__":
    main()