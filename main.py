import cherrypy
import simplejson
import wsgiref.handlers
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import memcache

from google.appengine.datastore import datastore_pb

from google.appengine.api import apiproxy_stub_map

DBNAME = 'Entity'

class KeyValue(datastore.Entity):
    """
    Datastore entity that has it's unindexed properties be a variable, not sure the performance
    implications of having an 'Entity' kind that could have ^n properties. 
    
    One advantage seems to assign both the keyname for the row, and the property name to the 
    same value. This could make searching much easier.
    
    feel free to destroy this, because it's a hacked mess.
    """
    def __init__(self,key,value=None):
        datastore.Entity.__init__(self,DBNAME,name=key)
        self[key] = value

class PathRoot:
    @cherrypy.expose
    def index(self):
        """
        function index, nothing to see here.
        """
        return "This is the HTTPDB Server."
    @cherrypy.expose
    def set(self, url_key=None, key_value=None):
        """
        function set, mapped to url: /set/$url_key/$key_value/
        params:
            @url_key: string to be saved in the datastore as the entity name
            @key_value: string to be saved as the value to the above key
        """
        try:
            entity = KeyValue(url_key,key_value)
            datastore.Put(entity)
        except:
            return "FAIL"
        return "SET"

    @cherrypy.expose
    def get(self, url_key=None):
        """
        function get, mapped to url: /get/$url_key/
        params:
            @url_key: string to be converted to datastore key
        """
        if url_key is None:
            return "{}"
        else:
            key = datastore_types.Key.from_path("Entity",url_key)
            try:
                """
                    PERFORM ASYNC RPC call to datastore.
                    check datastore._MakeSyncCall()
                    check apiproxy_stub_map.UserRPC()
                    
                    rpc = userrpc
                    rpc.make_call(blah)
                    ...
                    processing
                    ...
                    rpc.wait()
                    rpc.check_success()
                    
                """
                req = datastore_pb.GetRequest()
                req.add_key(key)
                rpc = datastore.CreateRPC()
                rpc.make_call()
                resp = 
                e = datastore.Get(key)
            except:
                return "{}"
            
            return simplejson.dumps(e)

def main():
    """
    Creating a cherrypy app using the PathRoot class as a root url handler.
    index, set & get are exposed to urls.
    """
    wsgiref.handlers.CGIHandler().run(cherrypy.tree.mount(PathRoot(),"/"))

if __name__ == '__main__':
  main()