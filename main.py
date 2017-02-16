import webapp2
import os
import jinja2

from google.appengine.ext import db

#setup jinja
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blogs(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)    

class MainPage(Handler):

    def get(self):
        self.redirect("/blog")

class Blog(Handler):

	def get(self):
		blog_posts = db.GqlQuery("SELECT * FROM Blogs ORDER BY created DESC LIMIT 5")
		t = jinja_env.get_template("blog.html")
		content = t.render(posts=blog_posts)
		self.response.write(content)


class NewPost(Handler):


	def get(self):
		t = jinja_env.get_template("entry.html")
		content = t.render()
		self.response.write(content)

	def post(self):
		title = self.request.get("title")
		post = self.request.get("post")

		if title and post:
			a = Blogs(title = title, post = post)
			a.put()

			self.redirect('blog/' + str(a.key().id()))
		else:
			error = "we need both a title and a blog post!"
			self.render("entry.html", title=title, post=post, error=error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        single_post = Blogs.get_by_id(int (id))
        t = jinja_env.get_template("post.html")
        content = t.render(post=single_post)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)