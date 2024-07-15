from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Access_reader, User


def index(request):
    users_list = User.objects.all()
    reader_list = Access_reader.objects.all()

    template = loader.get_template("idihaum/index.html")
    context = {
        "users_list": users_list,
        "reader_list": reader_list,
    }
    return HttpResponse(template.render(context, request))

# Create your views here.
def reader(request, reader_id):
    The_Reader = Access_reader.objects.get(id=reader_id)
    output = The_Reader.label
    return HttpResponse(output) # ("Info for Reader %s." % reader_id)

def user (request, user_id):
    The_User = User.objects.get(id = user_id)
    output = The_User.name
    return HttpResponse(output)
