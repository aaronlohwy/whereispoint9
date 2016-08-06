#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
from google.appengine.ext import db
import json

jinja_env = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class point9erlocation(db.Model):
    name = db.StringProperty(required=True)
    location = db.GeoPtProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now = True)
    
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self,template,**params):
		t=jinja_env.get_template(template)
		return t.render(params)
	def render(self,template,**kw):
		self.write(self.render_str(template,**kw))

class MainHandler(Handler):
    def get(self):
        point9locs = db.GqlQuery("SELECT * FROM point9erlocation ORDER BY created DESC") #can also do order by created DESC limit 10
        #point9locs = list(point9locs) #changes the cursor to a list, safer, prevent the running of multiple queries.
        point9locsjson=[]
        for entry in point9locs:
            jsondict = {"name": entry.name, "lat": entry.location.lat,"lon": entry.location.lon}
            jsonfile = json.dumps(jsondict)
            point9locsjson.append(jsonfile)
        #return jsonlist
        #self.write(point9locsjson)
        self.render("whereispoint9.html", point9locs = point9locsjson)

    def post(self):
        name = self.request.get("name")
        latitude = self.request.get("latitude")
        longitude = self.request.get("longitude")
        geopoint = db.GeoPt(float(latitude),float(longitude))

        if name and latitude and longitude:
            entry = point9erlocation(name=name, location=geopoint)
            entry.put()
            postID = entry.key().id() 
            #time.sleep(1) # not always good form to sleep, cuz you make the user wait. I put it just so when the page reloads the data is sure to be there! else the write might come before the art is put inside the database. it will eventually be consistent anyway. check out http://forums.udacity.com/questions/100044559/ascii-page-requires-a-reload-before-a-new-submission-is-displayed-why-ascii_chan-unit-3#cs253 
            #self.write(postID)
        else:
            self.write("ERROR YO")

        

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
