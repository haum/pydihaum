from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Access_reader, User, Card


def index(request):
    users_list = User.objects.all()
    reader_list = Access_reader.objects.all()

    template = loader.get_template("idihaum/index.html")
    context = {
        "users_list": users_list,
        "reader_list": reader_list,
    }
    return HttpResponse(template.render(context, request))


def reader(request, reader_id):
    the_reader = Access_reader.objects.get(id=reader_id)
    template = loader.get_template("idihaum/reader.html")
    context = {
		"the_reader": the_reader,
    }
    return HttpResponse(template.render(context, request))


def user (request, user_id):
    the_user = User.objects.get(id = user_id)
    template = loader.get_template("idihaum/user.html")
    context = {
		"the_user": the_user,
    }
    return HttpResponse(template.render(context, request))

