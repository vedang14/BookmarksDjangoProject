# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import RequestContext
from bookmarks.forms import *
from bookmarks.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
def main_page(request):
    # output = '''
    #     <html>
    #         <head><title>%s</title></head>
    #         <body>
    #             <h1>%s</h1><p>%s</p>
    #         </body>
    #     </html>
    # ''' % (
    #     'Django Bookmarks',
    #     'Welcome to Django Bookmarks',
    #     'Where you can store and share bookmarks!'
    # )
    # template = get_template('main_page.html')
    # Context = {
    #     # 'head_title' : 'Django Bookmarks',
    #     # 'page_title':  'Welcome to Django Bookmarks',
    #     # 'page_body' : 'Where you can store and share bookmarks!'
    #     'user' : request.user
    # }
    # output = template.render(Context)
    # return HttpResponse(output)

    return render(
        request,'main_page.html'
    )

def user_page(request,username):
    # try:
    #     user = get_object_or_404(User, username=username)
    # except:
    #     raise Http404('Requested user not found')
    # bookmarks = user.bookmark_set.all()
    # # template = get_template('user_page.html')
    # variable = {
    #     'username' : username,
    #     'bookmarks': bookmarks
    # }
    # # output = template.render(RequestContext)
    # # return HttpResponse(output)
    # return render(request,'user_page.html',variable)
    user = get_object_or_404(User, username=username)
    bookmarks = user.bookmark_set.order_by('-id')
    variables = {
    'bookmarks': bookmarks,
    'username': username,
    'show_tags': True,
    'show_edit': username == request.user.username,
    }
    return render(request,'user_page.html', variables)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid() :
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password1'],
                email = form.cleaned_data['email']
            )
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = { 'form' : form}
    return render(request,'registration/register.html',variables)     

def _bookmark_save(request,form):
     # Create or get link.
        link, dummy = Link.objects.get_or_create(
        url=form.cleaned_data['url']
        )
        # Create or get bookmark.
        bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        link=link
        )
        # Update bookmark title.
        bookmark.title = form.cleaned_data['title']
        # If the bookmark is being updated, clear old tag list.
        bookmark.tag_set.clear()
        # Create new tag list.
        tag_names = form.cleaned_data['tags'].split()
        for tag_name in tag_names:
            tag, dummy = Tag.objects.get_or_create(name=tag_name)
            bookmark.tag_set.add(tag)
        # Save bookmark to database.
        bookmark.save()
        return bookmark

@login_required(login_url= '/login/')
def bookmarks_save_page(request):
    ajax = request.GET.has_key('ajax')
    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        if form.is_valid():
            bookmark = _bookmark_save(request,form)
            if ajax:
                variables = {
                    'bookmarks' : [bookmark],
                    'show_edit' : True,
                    'show_tags': True
                }
                return render(request,'bookmark_list.html',variables)
            else:
                return HttpResponseRedirect('/user/%s/' %request.user.username)
        else: 
            if ajax:
                return HttpResponse('failure')
    elif request.GET.has_key('url'):
        url = request.GET['url']
        title= ''
        tags = ''
        try:
            link = Link.objects.get(url=url)
            bookmark = Bookmark.objects.get(
                link = link,
                user = request.user
            )
            title = bookmark.title
            tags = ''.join(
                tag.name for tag in bookmark.tag_set.all()
            )
        except ObjectDoesNotExist:
            pass
        form = BookmarkSaveForm({
            'url' : url,
            'title' : title,
            'tags': tags
        })
    else:
        form = BookmarkSaveForm()
    variables =  {
            'form': form
            }
    if ajax:
        return render(request,'bookmark_save_form.html',variables)
    else:
        return render(request,'bookmark_save.html', variables)

def tag_page(request,tag_name):
    tag = get_object_or_404(Tag,name = tag_name)
    bookmarks = tag.bookmarks.order_by('-id')
    variables = {
        'bookmarks': bookmarks,
        'tag_name' : tag_name,
        'show_tags' : True,
        'show_user' : True
    }
    return render(request,'tag_page.html',variables)

def tag_cloud_page(request):
    MAX_WEIGHT = 5
    tags = Tag.objects.order_by('name')
    # Calculate tag, min and max counts.
    min_count = max_count = tags[0].bookmarks.count()
    for tag in tags:
        tag.count = tag.bookmarks.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count
    # Calculate count range. Avoid dividing by zero.
    range = float(max_count - min_count)
    if range == 0.0:
        range = 1.0
    # Calculate tag weights.
    for tag in tags:
        tag.weight = int(
        MAX_WEIGHT * (tag.count - min_count) / range
        )
        variables = {
        'tags': tags
        }
    return render(request,'tag_cloud_page.html', variables)

def search_pages(request):
    form = SearchForm()
    bookmarks = []
    show_results = False
    if request.GET.has_key('query'):
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query':query})
            bookmarks = Bookmark.objects.filter(title__icontains=query)[:10]
    variables = {
        'form' : form,
        'bookmarks': bookmarks,
        'show_results': show_results,
        'show_tags': True,
        'show_user': True
    }   
    if request.GET.has_key('ajax'):
        return render(request,'bookmark_list.html',variables)
    else:
        return render(request,'search.html',variables)

def ajax_tag_autocomplete(request):
    if(request.GET.has_key('g')):
        tags = \
            Tag.objects.filter(name__istartswith=request.GET['g'])[:10]
        return HttpResponse('\n'.join(tag.name for tag in tags))
    return HttpResponse();