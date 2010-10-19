'''
Created on Mar 15, 2010

@author: Mohamed Azmy
'''
from pixel.errors import SchemaError
import functools
import collections
import os
import inspect

_BASETYPES = [str, int, float]

namespace = collections.defaultdict(dict)

def indent(string, tab="    "):
    return (tab + string.replace(os.linesep, "%s%s" % (os.linesep, tab))).rstrip(tab)

class element(object):
    def __init__(self, t, optional=False, default=None, **kwargs):
        if not isinstance(t, type):
            raise SchemaError("Expecting type")
        
        self.__t = t
        self.__optional = optional
        self.__primitive = t in _BASETYPES
        self.__default = default
        self.__kwargs = kwargs
        
        if optional and not self.primitive and default:
            raise SchemaError("Only optional/primitive elements can have defaults")
        if kwargs and self.primitive:
            raise SchemaError("Extra params can only be used with XmlElememt and XmlListElement types")
    
    @property
    def kwargs(self):
        return self.__kwargs
        
    @property
    def default(self):
        return self.__default
        
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
        return self.type(*args, **kargs)
        
class attribute(element):
    def __init__(self, t, **args):
        element.__init__(self, t, **args)
        if not self.primitive:
            raise SchemaError("Attributes must be a str, int or float")

class collection(element):
    def __init__(self, t, **args):
        if not isinstance(t, (XmlElementMeta, XmlListElementMeta)):
            raise SchemaError("Expecting an XmlElement")
        
        element.__init__(self, t, **args)
    
    def getInstance(self,*args, **kargs):
        return TypedList(self.type)

class innertext(element):
    def __init__(self, **args):
        element.__init__(self, str, **args)

class Schema(object):
    def __init__(self, namespace, classname, baseschemas=(), **args):
        self.__namespace = namespace
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
        #validate elements types.
        #if this object has innertext set, no other elements should present.
        for elm in self.__elements.values():
            if isinstance(elm, innertext) and len(self.__elements) > 1:
                raise SchemaError("No other elements should present with innertext")
        
    @property
    def hasInnerText(self):
        return len(self.elements) == 1 and isinstance(self.elements.values()[0], innertext)
    
    @property
    def namespace(self):
        return self.__namespace
    
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
        s = "<%s%s" % (elname, "".join([' %s="%s"' % (att, getattr(obj, att)) for att in self.attributes.keys()]))
        if self.elements:
            if self.hasInnerText:
                elementName, _ = self.elements.items()[0]
                s += ">%s" % getattr(obj, elementName)
            else:
                s += ">%s" % os.linesep
                for elementName, elm in self.elements.iteritems():
                    if not hasattr(obj, elementName):
                        raise SchemaError("Object doesn't have attribute '%s'" % elementName);
                    
                    elval = getattr(obj, elementName)
                    if elm.primitive:
                        s += indent("<%(name)s>%(elval)s</%(name)s>" % {'name': elementName, 'elval': elval}) + os.linesep
                    else:
                        s += indent(elval.__str__(elementName))
                    
            s += "</%s>%s" % (elname, os.linesep)
        else:
            s += "/>%s" % os.linesep
        return s

class TypedListSchema(Schema):
    #def __init__(self, namespace="", classname, baseschemas, **args):
    #    Schema.__init__(self, "", "TypedList", [])
    
    def toxml(self, obj, elname=None):
        #if not isinstance(obj, TypedList):
        #    raise SchemaError("Object not of type 'TypedList'")
        elname = elname if elname else self.classname.lower()
        s = "<%s%s>%s" % (elname, "".join([' %s="%s"' % (att, getattr(obj, att)) for att in self.attributes.keys()]), os.linesep)
        for e in obj:
            s += indent(e._schema.toxml(e)) 
        s += "</%s>%s" % (elname, os.linesep)
        return s
        
class TypedList(list):
    _schema = TypedListSchema("", "TypedList", ())
    
    def __init__(self, t):
        if not isinstance(t, (XmlElementMeta, XmlListElementMeta)):
            raise SchemaError("Only XmlElement/XmlListElement types are supported")
        
        list.__init__(self)
        self.__t = t 
    
    def __finalize__(self):
        for i in self:
            if hasattr(i, '__xinit__') and callable(i.__xinit__):
                i.__xinit__()
                
    @property
    def namespace(self):
        return self.__t._schema.namespace
    
    @property
    def type(self):
        return self.__t
    
    def getType(self, tag=None):
        if not tag:
            return self.type
        else:
            ns = namespace[self.namespace]
            if tag.lower() not in ns:
                raise SchemaError("Type '%s' not found in namespace '%s'" % (tag, self.namespace))
            t = ns[tag.lower()]
            if self.type not in t.mro():
                raise SchemaError("Type '%s' is not a child of type '%s'" % (tag, self.type.__name__))
            
            return t
            
    def __setitme__(self, key, value):
        if not isinstance(obj, self.type):
            raise RuntimeError("Invalid type, expecting '%s'" % self.type)
        list[key] = value
        
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
        
        if '__init__' in classDict:
            raise SchemaError("__init__ is not supported for class %s, please use __xinit__ instead" % classname)
        
        if '__xinit__' in classDict:
            xargs = inspect.getargspec(classDict['__xinit__'])
            if len(xargs.args) - 1 != len(xargs.defaults if xargs.defaults else []): # -1 is to drop self from count
                raise SchemaError("All params to __xinit__ should has default values in class %s" % classname)
                
        ns = classDict['__ns__'] if '__ns__' in classDict else ''
        
        #setting the __init__ method to intialize memebers.    
        def init(self, *args, **kargs):
            """overrides the default class init funcion"""
            for name, factoryElement in self._schema.elements.iteritems():
                setattr(self, "__%s" % name, factoryElement.getInstance())
            for name, factoryElement in self._schema.attributes.iteritems():
                setattr(self, "__%s" % name, factoryElement.getInstance())
            
        classDict['__init__'] = init
        
        def get_att(self, name):
            return getattr(self, "__%s" % name)
        
        #reversed for functools to work as expected later.
        def set_att(t, name, self, value):
            setattr(self, "__%s" % name, t(value))
                    
        for name, elm in toinit.iteritems():
            if elm.primitive:
                #set_attr = lambda self, value, name: setattr(self, name, value)
                classDict[name] = property(functools.partial(get_att, name=name),
                    functools.partial(set_att, elm.type, name))
            else:
                classDict[name] = property(functools.partial(get_att, name=name))
        #setting the schema
        baseschemas = []
        for base in bases:
            if isinstance(base, XmlElementMeta):
                baseschemas.append(base._schema)
                if not ns and base._schema.namespace:
                    ns = base._schema.namespace #inherit the namespace, if not defined.
        
        classDict['_schema'] = Schema(ns, classname, baseschemas, **toinit)
        clazz = type.__new__(cls, classname, bases, classDict)
        namespace[ns][classname.lower()] = clazz
        return clazz

class XmlListElementMeta(type):
    def __new__(cls, classname, bases, classDict):
        if "__type__" not in classDict:
            raise SchemaError("Missing __type__ declaration")
        
        listType = classDict["__type__"]
        if not isinstance(listType, (XmlElementMeta, XmlListElementMeta)):
            raise SchemaError("__type__ should be XmlElement of XmlListElement")
        
        toinit = {}
        for name in classDict.keys():
            value = classDict[name]
            if isinstance(value, attribute):
                del classDict[name]
                toinit[name] = value
            elif isinstance(value, attribute):
                raise SchemaError("List Elements supports attributes only")
                
        if '__init__' in classDict:
            raise SchemaError("__init__ is not supported for class %s, please use __xinit__ instead" % classname)
        
        if '__xinit__' in classDict:
            xargs = inspect.getargspec(classDict['__xinit__'])
            if len(xargs.args) - 1 != len(xargs.defaults if xargs.defaults else []): # -1 is to drop self from count
                raise SchemaError("All params to __xinit__ should has default values in class %s" % classname)
        
        ns = classDict['__ns__'] if '__ns__' in classDict else ''
        
        #setting the __init__ method to intialize memebers.    
        def init(self, *args, **kargs):
            """overrides the default class init funcion"""
            for name, factoryElement in self._schema.attributes.iteritems():
                setattr(self, "__%s" % name, factoryElement.getInstance())
            self._items = TypedList(listType)
            
            
        classDict['__init__'] = init
        
        def get_att(self, name):
            return getattr(self, "__%s" % name)
        
        #reversed for functools to work as expected later.
        def set_att(t, name, self, value):
            setattr(self, "__%s" % name, t(value))
                    
        for name, elm in toinit.iteritems():
            if elm.primitive:
                #set_attr = lambda self, value, name: setattr(self, name, value)
                classDict[name] = property(functools.partial(get_att, name=name),
                    functools.partial(set_att, elm.type, name))
            else:
                classDict[name] = property(functools.partial(get_att, name=name))
        #setting the schema
        baseschemas = []
        for base in bases:
            if isinstance(base, XmlListElementMeta):
                baseschemas.append(base._schema)
                if not ns and base._schema.namespace:
                    ns = base._schema.namespace #inherit the namespace, if not defined.
        
        classDict['_schema'] = TypedListSchema(ns, classname, baseschemas, **toinit)
        clazz = type.__new__(cls, classname, bases, classDict)
        namespace[ns][classname.lower()] = clazz
        return clazz

class XmlElement(object):
    __metaclass__ = XmlElementMeta

    def __str__(self, elementName=None):
        return self._schema.toxml(self, elementName)

class XmlListElement(object):
    __metaclass__ = XmlListElementMeta
    __type__ = XmlElement
    
    def __finalize__(self):
        for i in self:
            if hasattr(i, '__xinit__') and callable(i.__xinit__):
                i.__xinit__()
        
    def getType(self, tag=None):
        return self._items.getType(tag)
        
    def append(self, item):
        self._items.append(item)
    
    def insert(self, i, item):
        self._items.insert(i, item)
        
    def __setitme__(self, i, value):
        self._items[i] = value
    
    def __getitem__(self, i):
        return self._items[i]
        
    def __iter__(self):
        for e in self._items:
            yield e
    
    def __len__(self):
        return len(self._items)
        
    def __str__(self, elementName=None):
        elementName
        return self._schema.toxml(self, elementName)
