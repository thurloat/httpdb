import cherrypy
import simplejson
import wsgiref.handlers
from google.appengine.api import datastore
from google.appengine.api import datastore_types

class KeyValue(datastore.Entity):
    def __init__(self,key,value=None):
        datastore.Entity.__init__(self,'Entity',name=key)
        self[key] = value

class PathRoot:
    @cherrypy.expose
    def index(self):
        return "This is the HTTPDB Server."
    @cherrypy.expose
    def set(self, getValue=None, setValue=None):
        try:
            entity = KeyValue(getValue,setValue)
            entity.value = setValue
            datastore.Put(entity)
        except:
            return "FAIL"
        return "SET"

    @cherrypy.expose
    def get(self, getValue=None):
        key = datastore_types.Key.from_path("Entity",getValue)
        try:
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