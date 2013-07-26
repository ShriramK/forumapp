from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from forum.models import Forum, Thread, Post, UserProfile, User
from PIL import Image as PImage
from os.path import join as pjoin


def main(request):
	"""Main listing."""
	forums = Forum.objects.all()
	return render_to_response("forum/list.html", dict(forums=forums, user=request.user))

def forum(request, pk):
	"""Listing of threads in a forum."""
	threads = Thread.objects.filter(forum=pk).order_by("-created")
	threads = mk_paginator(request, threads, 20)
	return render_to_response("forum/forum.html", add_csrf(request, threads=threads, pk=pk))

def thread(request, pk):
	"""Listing of posts in a thread."""
	posts = Post.objects.filter(thread=pk).order_by("created")
	posts = mk_paginator(request, posts, 15)
	title = Thread.objects.get(pk=pk).title
	t = Thread.objects.get(pk=pk)
	return render_to_response("forum/thread.html", add_csrf(request, posts=posts, pk=pk,
		title=t.title, forum_pk=t.forum.pk, media_url=settings.MEDIA_URL))

def post(request, ptype, pk):
	"""Display a post form."""
	action = reverse("forum.views.%s" % ptype, args=[pk])
	if ptype == "new_thread":
		title = "Start New Topic"
		subject = ''
	elif ptype == "reply":
		title = ''
		subject = "Re: " + Thread.objects.get(pk=pk).title

	return render_to_response("forum/post.html", add_csrf(request, subject=subject, 
		action=action, title=title))

def new_thread(request, pk):
	"""Start a new thread."""
	p = request.POST 
	if p["subject"] and p["body"]:
		forum = Forum.objects.get(pk=pk)
		thread = Thread.objects.create(forum=forum, title=p["subject"], 
			creator=request.user)
		Post.objects.create(thread=thread, title=p["subject"], body=p["body"], 
			creator=request.user)
		increment_post_counter(request)
	return HttpResponseRedirect(reverse("forum.views.forum", args=[pk]))

def reply(request, pk):
	"""Reply to a thread."""
	p = request.POST
	if p["body"]:
		thread = Thread.objects.get(pk=pk)
		post = Post.objects.create(thread=thread, title=p["subject"], body=p["body"],
			creator=request.user)
		increment_post_counter(request)
	return HttpResponseRedirect(reverse("forum.views.thread", args=[pk]) + "?page=last")

@staff_member_required
def media(request):
	f = None
	actualPath = settings.MEDIA_ROOT + "\\images"
	imageName = request.path.split("/")
	actualPath += "\\" + imageName[len(imageName)-1]
	actualPath = actualPath.replace('\\', '/')
	f = open(actualPath, 'rb')
	if '.jpg' in request.path:
		imageTypeValue = "image/jpeg"
	elif '.png' in request.path:
		imageTypeValue = "image/png"
	return HttpResponse(f.read(), mimetype=imageTypeValue)

class ProfileForm(ModelForm):
	class Meta:
		model = UserProfile
		exclude = ["posts", "user"]

@login_required
def profile(request, pk):
	"""Edit user profile."""
	# As per http://stackoverflow.com/a/5478127/465974
	u = User.objects.get(id=pk)
	profile, created = UserProfile.objects.get_or_create(user=u)#user=pk)
	img = None

	if request.method == "POST":
		profile.avatar = request.POST.get("avatar")
		profile.save()
		pf = ProfileForm(request.POST, request.FILES, instance=profile)
		if pf.is_valid():
			pf.save()
			# resize and save image under same filename
			imfn = pjoin(settings.MEDIA_ROOT, profile.avatar.name)
			im = PImage.open(imfn)
			im.thumbnail((160, 160), PImage.ANTIALIAS)
			im.save(imfn, "JPEG")
	else:
		pf = ProfileForm(instance=profile)

	if profile.avatar:
		print 'profile.avatar exists'
		img = "/media/" + profile.avatar.name
	return render_to_response("forum/profile.html", add_csrf(request, pf=pf, img=img))
'''
def save_profile(request, pk):
	"""Save to a profile."""
	print 'request.META["HTTP_REFERER"]'
	print request.META["HTTP_REFERER"]
	p = request.POST
	print 'p'
	print p
	avatarName = request.POST["avatar"]
	if avatarName:
		imfname = os.path.join(settings.MEDIA_ROOT, avatarName)
		im = PImage.open(imfname, 'rb')
		im.thumbnail((160, 160), PImage.ANTIALIAS)

		imageTypeValue = None
		if '.jpg' in avatarName:
			imageTypeValue = "JPEG"
		elif '.png' in request.path:
			imageTypeValue = "PNG"

		im.save(imfname, "imageTypeValue")
		userProfileObj = UserProfile.objects.get(pk=pk)
		userProfileObj.avatar.save()

	return HttpResponseRedirect(request.META["HTTP_REFERER"])
'''

''' Helper Functions '''
def add_csrf(request, ** kwargs):
	d = dict(user=request.user, ** kwargs)
	d.update(csrf(request))
	return d

def mk_paginator(request, items, num_items):
	"""Create and return a paginator"""
	paginator = Paginator(items, num_items)
	try:
		page = int(request.GET.get("page", '1'))
	except ValueError:
		page = 1

	try:
		items = paginator.page(page)
	except (InvalidPage, EmptyPage):
		items = paginator.page(paginator.num_pages)
	return items

def increment_post_counter(request):
	profile = request.user.userprofile_set.all()[0]
	profile.posts += 1
	profile.save()

# TODO: Implement Full-Text Search
def search(request):
	results = None
	if request.method == "POST":
		results = Post.objects.all()
		p = request.POST
		for k, v in p.items():
			if k == 'myquery':
				results = results.filter(body__icontains=v)
	return render_to_response("forum/search.html", add_csrf(request, results=results))
