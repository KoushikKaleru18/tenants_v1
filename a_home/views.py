from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Item
from django.db import connection


def home_view(request):
    items = Item.objects.all()
    context = {
        'items': items
    }
    print("SCHEMA:", connection.schema_name)
    return render(request, 'home.html', context)


def create_item(request):
    if request.method == 'POST':
        if request.POST.get("name") != "":
            name = request.POST.get("name")
            item = Item(name=name)
            item.save()

            return HttpResponse(f'<li class="text-8xl font-thin">{ item.name }</li>')
        else:
            return HttpResponse('')

    else:
        return redirect('home')