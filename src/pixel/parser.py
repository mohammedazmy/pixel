'''
Created on Mar 15, 2010

@author: Mohamed Azmy
'''
from xml import sax
from errors import SchemaError, XmlLoadError
from xmlelement import XmlElement


class PixelHandler(sax.ContentHandler):
    class PrimitiveDataHolder(object):
        def __init__(self, name):
            self.name = name
            self.data = ''
        
    def __init__(self, ptype):
        sax.ContentHandler.__init__(self)
        if XmlElement not in ptype.mro():
            raise RuntimeError("ptype must be an XmlElement type")
        self.ptype = ptype
        self.reset()
    
    def reset(self):
        self.obj = None
        self.current = None
        self.stack = None
        self.characterMode = False
        
    def startElement(self, name, attrs):
        primitive = False
        if not self.stack:
            #first element. initialize with ptype
            obj = self.ptype()
            self.obj = obj
        else:
            parent = self.stack[len(self.stack) - 1] # last object
            #TODO: Very dirty using hardcoded names
            
            if parent._schema.classname == "TypedList":
                obj = parent.type() #create a new object of the list type
                parent.append(obj)
            else:
                if name not in parent._schema.elements:
                    raise SchemaError("Object of type '%s' doesn't have child object '%s'" % (type(parent),name))
                
                elm = parent._schema.elements[name]
                if elm.primitive:
                    primitive = True
                    self.characterMode = True
                    obj = self.PrimitiveDataHolder(name)
                else:
                    obj = getattr(parent, name)

        if not primitive:
            for attr_name, attr_element in obj._schema.attributes.iteritems():
                if not attr_element.optional and attr_name not in attrs:
                    raise XmlLoadError("Missing required attribute '%s' on element '%s'" % (attr_name, name))
                attr_val = attrs[attr_name]
                if not hasattr(obj, attr_name):
                    raise SchemaError("Object of type '%s' doesn't have attribute '%s'" % (type(obj), attr_name))
                setattr(obj, attr_name, attr_val)
            
        self.stack.append(obj)
    
    def endElement(self, name):
        obj = self.stack.pop()
        if self.characterMode:
            parent = self.stack[len(self.stack) - 1]
            setattr(parent, obj.name, obj.data)
            self.characterMode = False
            
    def startDocument(self):
        self.reset()
        self.obj = self.ptype()
        self.stack = []
    
    def endDocument(self):
        pass
    
    def characters(self, data):
        #dirty
        if self.characterMode:
            obj = self.stack[len(self.stack) - 1]
            obj.data += data
    
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
    
