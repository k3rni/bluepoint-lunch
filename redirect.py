from google.appengine.ext import webapp

class Redir(webapp.RequestHandler):
  def get(self, *args):
    self.response.headers.add_header('Location', 'http://4smaki.pl')
    self.response.set_status(301)

application = webapp.WSGIApplication([
        ('^/$', Redir),

    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
