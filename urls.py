from django.conf.urls import patterns, include, url

urlpatterns = patterns('forum.views',
	#url(r"^save_profile/(\d+)/$", "save_profile"),
	url(r"^search/$", "search"),
	url(r"^profile/(\d+)/$", "profile"),
	url(r"^post/(new_thread|reply)/(\d+)/$", "post"),
	url(r"reply/(\d+)/$", "reply"),
	url(r"new_thread/(\d+)/$", "new_thread"),
	url(r"^thread/(\d+)/$", "thread"),
	url(r"^forum/(\d+)/$", "forum"),
	url(r"^media/", "media"),
	url(r"", "main"),
)
