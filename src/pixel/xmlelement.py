'''
Created on Mar 15, 2010

@author: Mohamed Azmy
'''
from errors import SchemaError

class TypedList(list):
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
        


class element(object):
    def __init__(self, t):
        if not isinstance(t, type):
            raise SchemaError("Expecting type")
        
        self.__t = t
    
    @property
    def type(self):
        return self.__t
    
    def getInstance(self):
        return self.type()

class attribute(element):
    pass

class collection(element):
    def getInstance(self):
        return TypedList(self.type)

class Schema(object):
    def __init__(self, baseschemas=(), **args):
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
        
        classDict['_schema'] = Schema(baseschemas, **toinit)
        
        #setting up the __str__ method.
        def _str(self):
            s = "<%s%s>\n" % (classname, " ".join(["%s='%s'" % (n, getattr(self, n)) for n in self._schema.attributes.keys()]))
            for elemname, elem in self._schema.elements.iteritem():
                if isinstance(elem, collection):
                    pass
                else:
                    pass
                
            s += "<%s>\n" % classname
        
        return type.__new__(cls, classname, bases, classDict)

class XmlElement(object):
    __metaclass__ = XmlElementMeta
    
    def __init__(self):
        pass
