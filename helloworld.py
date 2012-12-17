import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users

class Greeting(db.Model):
    """Models an individual Guestbook entry with an author, content and date."""
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

def guestbook_key(guestbook_name=None):
    """
    Constructs a Datastore key for a Guestbook entity with guestbook_name.
    """
    # From the from_path help text: 'Guestbook' is the "kind" of the key and
    # guestbook_name is the "name". If guestbook_name were an int, it would be
    # the "id". These can be retrieved from the key by the .kind(), .name() and
    # .id() methods.
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name')
        greeting_query = Greeting.all().ancestor(
            guestbook_key(guestbook_name)).order('-date')
        greetings = greeting_query.fetch(10)

        for greeting in greetings:
            if greeting.author:
                self.response.out.write('<b>%s</b> wrote:' % greeting.author)
            else:
                self.response.out.write('An anonymous person wrote:')
            self.response.out.write('<blockquote>%s</blockquote>' %
                                    cgi.escape(greeting.content))

        self.response.out.write("""
            <form action="/sign?%s" method="post">
                <div><textarea name="content" rows="3" cols="60"></textarea>
                </div>
                <div><input type="submit" value="Sign guestbook"></div>
            </form>
            <hr>
            <form>Guestbook name: <input value="%s" name="guestbook_name">
                <input type="submit" value="switch"></form>
        </body></html>""" % (
            urllib.urlencode({'guestbook_name': guestbook_name}),
            cgi.escape(guestbook_name)))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user().nickname()

        greeting.content = self.request.get('content')
        greeting.put()

        self.redirect('/?' + urllib.urlencode({'guestbook_name':
                                               guestbook_name}))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/sign', Guestbook)],
                              debug=True)
