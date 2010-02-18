import cherrypy
import wsgiref.handlers

class PathRoot:
    @cherrypy.expose
    def index(self):
        return "This is the HTTPDB Server."

class PathGet:
    @cherrypy.expose
    def index(self):
        return "{'key':'value','http':'db'}"

def main():
  root = PathRoot()
  root.get = PathGet()
  app = cherrypy.tree.mount(root,"/")
  wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
  main()