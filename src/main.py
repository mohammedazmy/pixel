
from xml import sax
from pixel.xmlelement import XmlElement, element, collection, attribute

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
    pass
    

if __name__ == "__main__":
    main()