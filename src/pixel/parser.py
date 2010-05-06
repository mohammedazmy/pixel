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
    
    class Status(object):
        def __init__(self):
            self.populated = []
        
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
            parent, status = self.stack[len(self.stack) - 1] # last object
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
                
                status.populated.append(name)

        if not primitive:
            attr_names = attrs.keys()
            for attr_name, attr_element in obj._schema.attributes.iteritems():
                if attr_element.optional and attr_name not in attrs:
                    continue
                elif attr_name not in attrs:
                    raise XmlLoadError("Missing required attribute '%s' on element '%s'" % (attr_name, name))
                    
                attr_val = attrs[attr_name]
                attr_names.remove(attr_name)
                if not hasattr(obj, attr_name):
                    raise SchemaError("Object of type '%s' doesn't have attribute '%s'" % (type(obj), attr_name))
                setattr(obj, attr_name, attr_val)
            if attr_names:
                raise XmlLoadError("Found attributes '%s' which are not defined in the schema of elemenmt '%s'" % (", ".join(attr_names), name))
                
        self.stack.append((obj, self.Status()))
    
    def endElement(self, name):
        obj, status = self.stack.pop()
        if self.characterMode:
            parent = self.stack[len(self.stack) - 1][0]
            setattr(parent, obj.name, obj.data)
            self.characterMode = False
        else:
            #validate ended object.
            #Make sure that all (not optional) sub objects has been found there.
            for sub, elm in obj._schema.elements.iteritems():
                if sub not in status.populated and not elm.optional:
                    raise XmlLoadError("Opject '%s' requires subobject '%s'" % (name, sub))
                
            
    def startDocument(self):
        self.reset()
        self.obj = self.ptype()
        self.stack = []
    
    def endDocument(self):
        pass
    
    def characters(self, data):
        #dirty
        if self.characterMode:
            obj, status = self.stack[len(self.stack) - 1]
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
    
