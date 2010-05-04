'''
Created on Mar 15, 2010

@author: Mohamed Azmy
'''
from errors import SchemaError
_BASETYPES = [str, int, float]

class element(object):
    def __init__(self, t, optional=False):
        if not isinstance(t, type):
            raise SchemaError("Expecting type")
        
        self.__t = t
        self.__optional = optional
        self.__primitive = t in _BASETYPES
        
    @property
    def primitive(self):
        return self.__primitive
    
    @property
    def optional(self):
        return self.__optional
    
    @property
    def type(self):
        return self.__t
    
    def getInstance(self, *args, **kargs):
        if self.primitive:
            return PrimitiveXmlElement(self.type)
        else:
            return self.type(*args, **kargs)

class attribute(element):
    def __init__(self, t, optional=False):
        element.__init__(self, t, optional)
        if not self.primitive:
            raise SchemaError("Attributes must be a str, int or float")

class collection(element):
    def __init__(self, t):
        if not isinstance(t, XmlElementMeta):
            raise SchemaError("Expecting an XmlElement")
        
        element.__init__(self, t)
    
    def getInstance(self,*args, **kargs):
        return TypedList(self.type)

class Schema(object):
    def __init__(self, classname, baseschemas=(), **args):
        self.__classname = classname
        self.__attrs = {}
        self.__elements = {}
        
        for baseschema in baseschemas:
            self.__attrs.update(baseschema.attributes)
            self.__elements.update(baseschema.elements)
        
        for k, v in args.iteritems():
            if not isinstance(v, element):
                raise SchemaError("Invalid element type '%s'" % k)
            
            if isinstance(v, attribute):
                self.__attrs[k] = v
            else:
                self.__elements[k] = v
    
    @property
    def attributes(self):
        return self.__attrs
    
    @property
    def elements(self):
        return self.__elements
    
    @property
    def classname(self):
        return self.__classname
    
    def toxml(self, obj, elname=None):
        elname = elname if elname else self.classname.lower()
        s = "<%s%s>" % (elname, "".join([' %s="%s"' % (att, getattr(obj, att).value) for att in self.attributes.keys()]) if self.elements else "")
        for elementName, element in self.elements.iteritems():
            if not hasattr(obj, elementName):
                raise SchemaError("Object doesn't have attribute '%s'" % elementName);
            
            elval = getattr(obj, elementName)
            s += elval.__str__(elementName)
        s += "</%s>" % elname
        return s

class TypedListSchema(Schema):
    def __init__(self):
        Schema.__init__(self, "TypedList", [])
    
    def toxml(self, obj, elname):
        if not isinstance(obj, TypedList):
            raise SchemaError("Object not of type 'TypedList'")
        
        s = "<%s>" % elname
        for e in obj:
            s += e._schema.toxml(e) 
        s += "</%s>" % elname
        return s
        
class TypedList(list):
    _schema = TypedListSchema()
    
    def __init__(self, t):
        list.__init__(self)
        self.__t = t
    
    @property
    def type(self):
        return self.__t
    
    def append(self, obj):
        if not isinstance(obj, self.type):
            raise RuntimeError("Invalid type, expecting '%s'" % self.type)
        list.append(self, obj)
    
    def insert(self, index, obj):
        if not isinstance(obj, self.type):
            raise RuntimeError("Invalid type, expecting '%s'" % self.type)
        list.insert(self, index, obj)
    
    def __str__(self, elementName):
        return self._schema.toxml(self, elementName)
    
class XmlElementMeta(type):
    def __new__(cls, classname, bases, classDict):
        toinit = {}
        for name in classDict.keys():
            value = classDict[name]
            if isinstance(value, element):
                del classDict[name]
                toinit[name] = value
            
        __init = None        
        if '__init__' in classDict:
            __init = classDict['__init__']
        
        #setting the __init__ method to intialize memebers.    
        def init(self, *args, **kargs):
            """overrides the default class init funcion"""
            for name, factoryElement in self._schema.elements.iteritems():
                setattr(self, name, factoryElement.getInstance())
            for name, factoryElement in self._schema.attributes.iteritems():
                setattr(self, name, factoryElement.getInstance())
            
            if __init:
                __init(self, *args, **kargs)
                
        classDict['__init__'] = init
        
        #setting the schema
        baseschemas = []
        for base in bases:
            if isinstance(base, XmlElementMeta):
                baseschemas.append(base._schema)
        
        classDict['_schema'] = Schema(classname, baseschemas, **toinit)
        return type.__new__(cls, classname, bases, classDict)

class XmlElement(object):
    __metaclass__ = XmlElementMeta

    def __str__(self, elementName=None):
        return self._schema.toxml(self, elementName)

class PrimitiveXmlElement(XmlElement):
    def __init__(self, t, *args):
        self.__type = t
        self.__value = t(*args)
    
    @property
    def type(self):
        return self.__type
    
    def __getValue(self):
        return self.__value
    def __setValue(self, v):
        self.__value = self.__type(v)
    
    value = property(__getValue, __setValue)
    
    def __str__(self, elementName):
        return "<%(elname)s>%(elvalue)s</%(elname)s>" % {'elname': elementName, 'elvalue': self.value}