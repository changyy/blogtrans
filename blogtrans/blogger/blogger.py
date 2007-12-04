try:
  from xml.etree import ElementTree # for Python 2.5 users
except:
  from elementtree import ElementTree
from gdata import service
import gdata
import atom
import getopt
import sys

from blogtrans.data import *
from datetime import datetime

class Blogger:
  def __init__(self, email, password):
    
    self.service = service.GDataService(email, password)
    self.service.source = 'BlogTrans'
    self.service.service = 'blogger'
    self.service.server = 'www.blogger.com'
    self.service.ProgrammaticLogin()

    query = service.Query()
    query.feed = '/feeds/default/blogs'
    feed = self.service.Get(query.ToUri())
    
    self.blogids = []
    self.blognames = []
    
    # Print the results.
    print feed.title.text
    for entry in feed.entry:
      blog_id = entry.GetSelfLink().href.split('/')[-1]
      blog_name = entry.title.text
      print blog_id+"\t" + blog_name
      self.blogids.append( blog_id )
      self.blognames.append( blog_name )
      
  def SelectBlog(self, n) :
    self.blog_id = self.blogids[n]

  def CreatePost(self, article):
  
    # Create the entry to insert.
    entry = gdata.GDataEntry()
    entry.author.append(atom.Author(atom.Name(text=article.author)))

    #timetext = article.date.strftime("%Y
    # to be modified    
    # entry.published = atom.Published(text="2006-11-08T18:10:00.000-08:00")
    # entry.updated = atom.Updated(text="2006-11-08T18:10:00.000-08:00")
    
    datetext = article.date.strftime("%Y-%m-%dT%I:%M:%S.000-08:00")
    entry.published = atom.Published(datetext)
    entry.updated = atom.Updated(datetext)
   
    entry.title = atom.Title(title_type='xhtml', text=article.title)
    entry.content = atom.Content(content_type='html', text=article.body)
    
    if article.status!=article.PUBLISH :
      control = atom.Control()
      control.draft = atom.Draft(text='yes')
      entry.control = control

    # Ask the service to insert the new entry.
    return self.service.Post(entry, '/feeds/' + self.blog_id + '/posts/default')

  def CreateComment(self, post_id, comment):
    # Build the comment feed URI
    feed_uri = '/feeds/' + self.blog_id + '/' + post_id + '/comments/default'

    # Create a new entry for the comment and submit it to the GDataService
    entry = gdata.GDataEntry()
    #atom.Author(atom.Name(text="Tester"))
    entry.content = atom.Content(content_type='xhtml', text=comment.body)
    return self.service.Post(entry, feed_uri)
