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
    try:
        user = User.objects.get(username=username)
    except:
        raise Http404('Requested user not found')
    bookmarks = user.bookmark_set.all()
    # template = get_template('user_page.html')
    variable = RequestContext(request,{
        'username' : username,
        'bookmarks': bookmarks
    })
    # output = template.render(RequestContext)
    # return HttpResponse(output)
    return render(request,'user_page.html',variable)

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