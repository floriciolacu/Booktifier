from django.conf.urls import url
from booktifier import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	url(r'^$', views.FrontPageView.as_view(), name = 'home'),
	url(r'^books/$', views.BooksListView.as_view(), name = 'bookslist'),
    url(r'^author/add/$', views.AuthorCreateView.as_view(), name='author_create'),
    url(r'^author/(?P<pk>[0-9]+)/$', views.AuthorDetailView.as_view(), name='author_detail'),
    url(r'^book/(?P<pk>[0-9]+)/$', views.BookDetailView.as_view(), name = 'book_detail'),
    url(r'^book/(?P<pk>[0-9]+)/delete$',  views.BookDeleteView.as_view(), name='book_delete'),
    url(r'^book/add/$', views.BookCreateView.as_view(), name='book_create'),
    url(r'^book/(?P<pk>[0-9]+)/update$', views.BookUpdateView.as_view(), name='book_update'),
    url(r'^book/(?P<pk>[0-9]+)/voted/(?P<value>[0-5])/$', views.AddedScoreView.as_view(), name='voted'),
	url(r'^book/(?P<pk>[0-9]+)/bookcomment/$', views.add_comment_to_book, name = 'bookcomment'),
    url(r'^book/(?P<pk>[0-9]+)/favorite/(?P<value>[0-9]+)/$', views.AddedFavoriteView.as_view(), name='favorite'),
	url(r'^book/(?P<pk>[0-9]+)/read/(?P<value>[0-9]+)/$', views.AddedReadView.as_view(), name='read'),
    url(r'^login/$', views.login_view, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^search/(?P<input>[A-Za-z]+)/$', views.SearchPageListView.as_view(), name="search"),
    url(r'^search/$', views.SearchPageListView1.as_view(), name="search1"),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.UserProfileDetailView.as_view(), name='profile'),
    url(r'^register/$', views.signup, name="register"),
	url(r'^profile/(?P<pk>[0-9]+)/update/$', views.update_profile, name='profile_update'),
    url(r'^upload/$', views.upload_file, name="upload"),
    url(r'^prediction/(?P<bname>.*)/$', views.FindPageListView.as_view(), name="prediction"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
