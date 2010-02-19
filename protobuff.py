#!/usr/bin/env python
# encoding: utf-8
"""
protobuff.py

Created by Adam on 2010-02-19.
Copyright (c) 2010 NOREX. All rights reserved.
"""

from google.net.proto import ProtocolBuffer
import dummy_thread as thread
from google.appengine.datastore.entity_pb import EntityProto

from google.appengine.datastore import datastore_pb
from google.appengine.datastore import entity_pb

class HttpDbJsonPropertyValue(entity_pb.PropertyValue):
    def __json__(self):
        return self.DebugFormatString(self.stringvalue_)
        
class HttpDbJsonProperty(entity_pb.Property):
    def __init__(self, contents=None):
        self.value_ = HttpDbJsonPropertyValue()
        if contents is not None: self.MergeFromString(contents)
        
    def __json__(self):
        js = {}
        if self.has_name_ & self.has_value_:
            js[self.DebugFormatString(self.name_)] = self.value_.__json__()
        return js

class HttpDbJsonEntityProto(entity_pb.EntityProto):
    def add_property(self):
        x = HttpDbJsonProperty()
        self.property_.append(x)
        return x
    def add_raw_property(self):
        x = HttpDbJsonProperty()
        self.raw_property_.append(x)
        return x

class HttpDbResponse_Entity(datastore_pb.GetResponse_Entity):
    def entity(self):
        if self.entity_ is None:
            self.lazy_init_lock_.acquire()
            try:
                if self.entity_ is None: self.entity_ = HttpDbJsonEntityProto()
            finally:
                self.lazy_init_lock_.release()
        return self.entity_
    def __json__(self):
        js = []
        for x in self.entity().property_list():
            js.append(x.__json__())
        return js

class HttpDbResponse(ProtocolBuffer.ProtocolMessage):
    def __init__(self, contents=None):
        self.entity_ = []
        self.buffstring = contents
    def entity_size(self): return len(self.entity_)
    def entity_list(self): return self.entity_
    def entity(self, i):
        return self.entity_[i]
    def Clear(self):
        self.buffstring = None
    def IsInitialized(self,debug_strs=None):
        return 1
    def __str__(self,prefix="",printElemNumber=0):
        return self.buffstring
    def add_entity(self):
        x = HttpDbResponse_Entity()
        self.entity_.append(x)
        return x
    def mutable_entity(self, i):
        return self.entity_[i]
    def OutputUnchecked(self, out):
        for i in xrange(len(self.entity_)):
            out.putVarInt32(11)
            self.entity_[i].OutputUnchecked(out)
            out.putVarInt32(12)
    def __str__():
        return "HttpDbResponse ..."
    def Equals(self,other):
        if x is self: return 1
        if len(self.entity_) != len(x.entity_): return 0
        for e1, e2 in zip(self.entity_,x.entity_):
            if e1 != e2: return 0
        return 1
    def TryMerge(self,d):
         while d.avail() > 0:
           tt = d.getVarInt32()
           if tt == 11:
             self.add_entity().TryMerge(d)
             continue
           if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
           d.skipData(tt)
    def MergeFrom(self,d):
         assert x is not self
         for i in xrange(x.entity_size()): self.add_entity().CopyFrom(x.entity(i))
    

class HttpDbRequest(datastore_pb.GetRequest):
    def foo(self):
        return "bar"