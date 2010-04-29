
from xml import sax
from pixel.xmlelement import XmlElement, element, collection, attribute

class MyHandler(sax.ContentHandler):
    def __init__(self):
        sax.ContentHandler.__init__(self)
    
    def startElement(self, name, attrs):
        print "Start element %s" % name
        for item in attrs.items():
            print item
    
    def endElement(self, name):
        print "End element %s" % name
        
    def startDocument(self):
        print "Start Document"
    
    def endDocument(self):
        print "End Document"


class Info(XmlElement):
    name = element(str)
    age = element(int)

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
    packages = collection(Package)
    
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
        <Element name='name' data='fuck'>Azmy</Element>
        <Element name='age'/>
    </elements>
</main>""", MyHandler())
    

if __name__ == "__main__":
    main()