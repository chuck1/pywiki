#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cgitb
cgitb.enable()

import os
import cgi
import jinja2
import markdown


# modes:
#     new page creation: 'page' set but not file exists
#     page edit
#     homepage
#     page view

#dir_pre = "/home/chuck/Git/wiki_cgi_test/"

dir_lib,_ = os.path.split(__file__)

#head1 = "<link href=\"http://web.engr.oregonstate.edu/~rymalc/default.css\" rel=\"stylesheet\"></link>"
head1 = "<link href=\"http://127.0.0.1/style.css\" rel=\"stylesheet\"></link>"

def mdrend(raw):
	return markdown.markdown(raw, extensions=['extra', 'tables'])



def path2list(p):
	l = []
	
	for i in range(5):
		p,t = os.path.split(p)
		if not t:
			break
		if t == '.':
			break
		l.insert(0,t)
		#print p,t
		
	return l

def getbranch(d, l):
	
	while l:
		a = l.pop(0)
		try:
			d = d[a]
		except:
			d[a] = {}
			d = d[a]
	
	return d

def htmllist(d):
	
	print "<ul>\n"
	for k,v in d.items():
		print "<li>{}</li>".format(k)
		if v:
			htmllist(v)
			
	print "</ul>\n"
	

class Form(object):
	def __init__(self, dir_pre):

		self.dir_pre = dir_pre

		self.form = cgi.FieldStorage()

		#print self.form.list

		self.forms = {}
		
		self.topbar = "<h1>"+dir_pre+"</h1>"

		with open(os.path.join(dir_lib, 'templates/forms/go.html')) as f:
			self.html_form_go = f.read()
		with open(os.path.join(dir_lib, 'templates/forms/tree.html')) as f:
			self.html_form_tree = f.read()
		with open(os.path.join(dir_lib, 'templates/forms/textarea.html')) as f:
			self.forms["textarea"] = f.read()

		with open(os.path.join(dir_lib, 'templates/page.html')) as f:
			self.temp = jinja2.Template(f.read())

		self.data = {}
		self.data["submit"] = self.get("submit")
		self.data["page"] = self.get("page")
		self.data["mode"] = self.get("mode")
		self.data["raw"] = self.get("raw")

	def __getitem__(self, k):
		return self.form.__getitem__(k)

	def get(self, key):
		try:
			val = self.form[key].value
		except:
			val = None
		#print "{} = {}</br>".format(key, val)
		return val

	def homepage(self):
		#print head1
		#print "home page\n"
		
		#print self.html_form_tree
		#print self.html_form_go

		print head1

		htmltext = self.temp.render(
			head = head1,
			topbar = self.topbar,
			body = self.html_form_tree + self.html_form_go)
		
		print htmltext
	

	def page_edit(self, page, raw_file):


		topmatter = self.html_form_go
		topmatter += "<h1>" + page + "</h1>\n"
		
		#text_page_html = mdrend(raw_file)
		
		mode = self.data["mode"]
		submit = self.data["submit"]
		
		#if mode == Mode.page_edit_enter:
		if submit == "go":
			raw_form = raw_file
		else:
			if mode=="new":
				raw_form = raw_file
			elif mode=="edit":
				raw_form = self.data["raw"]
			else:
				print "error!"

		
		html_form = mdrend(raw_form)


		# jinja

		var = {"topbar":self.topbar, "page":page, "mode":mode, "text_form":raw_form}
		
		body = "<div>"+topmatter+"</div><div>"+html_form+"</div>"
		body += self.forms["textarea"]
		
		body = jinja2.Template(body).render(var)
		
		htmltext = self.temp.render(
			head=head1,
			topbar = self.topbar,
			body=body,
			page=page,
			mode="edit")
		
		print htmltext

	def page_new(self, page):
		topmatter = self.html_form_go
		topmatter += "<h1>new page: " + page + "</h1>\n"
	
		raw_form = self.data["raw"]

	
		if raw_form:
			html_form = mdrend(raw_form)
		else:
			html_form = ""
			raw_form = ""
		

		# jinja
		
		var = {"topbar":self.topbar, "page":page, "mode":"new", "text_form":raw_form}
		
		body = "<div>" + topmatter + "</div><div>" + html_form + "</div>"
		body += self.forms["textarea"]
	
		body = jinja2.Template(body).render(var)
		
		var["head"] = head1
		var["body"] = body
		
		htmltext = self.temp.render(var)
	
		print htmltext


	def page_tree(self):
		
		d = {}
		
		for root, dirs, files in os.walk(self.dir_pre):
			if not '.git' in root:
				root = os.path.relpath(root, self.dir_pre)
				
				#print 'root',root,"</br>"
				
				l = path2list(root)
				#print l, "</br>"
				
				b = getbranch(d, l)
				#print b, "</br>"

				for f in files:
					#f = os.path.join(root,f)
					#print root, f, "</br>"

					b[f] = None
				

		#print d, "</br>"

		htmllist(d)

	def readfile(self, page):

		if not page:
			return None

		filename = self.dir_pre + page + ".md"
		
		try:
			f = open(filename)
		except:
			raw_file = None
		else:
			raw_file = f.read()
			f.close()
		
		return raw_file

def run(dir_pre):

	print "Content-Type: text/html;charset=utf-8"
	print "Cache-Control: max-age=0, no-cache, no-store"
	print "expires: 0\n"

	form = Form(dir_pre)
	
	# data collection
	submit = form.data["submit"]
	page = form.data["page"]
	mode = form.data["mode"]
	raw = form.data["raw"]


	# data entry

	if submit=="save" and page and raw:
		
		p = os.path.join(dir_pre + page)
		d,_ = os.path.split(p)

		os.makedirs(d)

		with open(p + ".md", 'w') as f:
			f.write(raw)
	


	raw_file = form.readfile(page)
	#print "raw_file =",raw_file,"</br>"


	# page rendering



	# name of the button pressed
	
	if submit=="save":
		form.page_edit(page, raw_file)
	elif submit=="go":
		if page:
			if raw_file:
				form.page_edit(page, raw_file)
			else:
				form.page_new(page)
		else:
			form.homepage()
	elif submit=="preview":
		if mode=="new":
			form.page_new(page)
		elif mode=="edit":
			form.page_edit(page, raw_file)
		else:
			print "error"
	elif submit=="tree":
		form.page_tree()
	else:
		form.homepage()

	
	return

