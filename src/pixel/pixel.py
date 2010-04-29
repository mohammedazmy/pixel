'''
Created on Mar 15, 2010

@author: mazmi
'''
from xml import sax
from xmlelement import XmlElement

class PixelHandler(sax.ContentHandler):
    def __init__(self, ptype, ondocument):
        if XmlElement not in ptype.mro():
            raise RuntimeError("ptype must be an XmlElement type")
        self.ptype = ptype
        self.obj = None
        self.current = None
        self.stack = None
        self.ondocument = ondocument
        sax.ContentHandler.__init__(self)
    
    def startElement(self, name, attrs):
        print "Start element %s" % name
        
        for attname, attvalue in attrs.items():
            print attname, ": ", attvalue
    
    def endElement(self, name):
        print "End element %s" % name
        
    def startDocument(self):
        self.obj = self.ptype()
        self.stack = []
        self.current = self.obj
    
    def endDocument(self):
        self.ondocument(self.obj)
        
class XmlReader(object):
    def __init__(self, ptype):
        
        """
        @param ptype: The parent type of the document. 
        """
        self._ptype = ptype
    
    def parse(self, source):
        obj = None
        def setobj(o):
            obj = o
            
        handler = PixelHandler(self._ptype, setobj)
        
        
        return obj
    