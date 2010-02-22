import cherrypy
import wsgiref.handlers


from google.appengine.api import datastore
from google.appengine.api import datastore_types

from google.appengine.api import memcache

from google.appengine.datastore import datastore_pb
from google.appengine.api import apiproxy_stub_map

from cherrypy._cpdispatch import Dispatcher

from protobuff import HttpDbJsonPropertyValue, HttpDbJsonProperty, HttpDbJsonEntityProto, HttpDbResponse_Entity, HttpDbResponse, HttpDbRequest

DBNAME = 'Entity'

class HttpDbDispatcher(object):
    """
    this is our custom dispatcher which strips out the database name (first
    url part) and pass the rest of the url to the default dispatcher
    
    """
    dispatcher = Dispatcher()
    def __call__(self, path_info):
        list = path_info.strip('/').split('/', 1)
        
        #handle root url
        if len(list) < 2:
            self.dispatcher("/")
            return       
          
        DBNAME = list[0]
        self.dispatcher(list[1])


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
            key = datastore_types.Key.from_path(DBNAME,url_key)
           #try:
            req = datastore_pb.GetRequest()
            req.key_list().append(key._ToPb())
            rpc = datastore.DatastoreRPC('datastore_v3')
            resp = HttpDbResponse()
            rpc.make_call('Get',req,resp)
            
            import simplejson
            
            rpc.wait()
            rpc.check_success()
            e = resp.entity_list()
            
            return [simplejson.dumps(x.__json__()) for x in e]
            #except:
            #    return "{}"
    @cherrypy.expose
    def query(self, *args):
        return " | ".join(args)

def main():
    """
    Creating a cherrypy app using the PathRoot class as a root url handler.
    index, set & get are exposed to urls.
    """
    d = HttpDbDispatcher()
    conf = {'/': 
                {'request.dispatch': d} 
           }
    
    wsgiref.handlers.CGIHandler().run(cherrypy.tree.mount(PathRoot(),"/", conf))

if __name__ == '__main__':
    main()