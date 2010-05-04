'''
Created on Mar 15, 2010

@author: mazmi
'''
from xml import sax
from errors import SchemaError, XmlLoadError
from xmlelement import XmlElement


class PixelHandler(sax.ContentHandler):
    def __init__(self, ptype):
        sax.ContentHandler.__init__(self)
        if XmlElement not in ptype.mro():
            raise RuntimeError("ptype must be an XmlElement type")
        self.ptype = ptype
        self.obj = None
        self.current = None
        self.stack = None
    
    def startElement(self, name, attrs):
        if not self.stack:
            #first element. initialize with ptype
            obj = self.ptype()
            self.obj = obj
        else:
            parent = self.stack[len(self.stack) - 1] # last object
            #TODO: Very dirty using hardcoded names
            if parent._schema.classname == "TypedList":
                obj = parent.type()
                parent.append(obj)
            elif name not in parent._schema.elements:
                raise SchemaError("Object of type '%s' doesn't have child object '%s'" % (type(parent),name))
            else:
                obj = getattr(parent, name)
            
        for attr_name, attr_element in obj._schema.attributes.iteritems():
            if not attr_element.optional and attr_name not in attrs:
                raise XmlLoadError("Missing required attribute '%s' on element '%s'" % (attr_name, name))
            attr_val = attrs[attr_name]
            if not hasattr(obj, attr_name):
                raise SchemaError("Object of type '%s' doesn't have attribute '%s'" % (type(obj), attr_name))
            attr = getattr(obj, attr_name)
            attr.value = attr_val
            
        self.stack.append(obj)
    
    def endElement(self, name):
        self.stack.pop()
        #TODO: validate correctness.
        
    def startDocument(self):
        self.obj = self.ptype()
        self.stack = []
    
    def endDocument(self):
        pass
    
    def characters(self, data):
        obj = self.stack[len(self.stack) - 1]
        #dirty
        if obj._schema.classname == "PrimitiveXmlElement":
            obj.value = data
    
class XmlReader(object):
    def __init__(self, ptype):
        
        """
        @param ptype: The parent type of the document. 
        """
        self._ptype = ptype
    
    def parse(self, source):
        handler = PixelHandler(self._ptype)
        sax.parseString(source, handler)
        return handler.obj
    