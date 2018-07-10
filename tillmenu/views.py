from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django import forms
from django.urls import reverse

from .models import Menu, default_menu

from . import parser

class NewMenuForm(forms.Form):
    name = forms.CharField(max_length=80)

def index(request):
    menus = Menu.objects.all()

    if request.method == 'POST':
        form = NewMenuForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            nm = Menu(name=cd['name'], contents=default_menu)
            nm.save()
            return HttpResponseRedirect(nm.get_absolute_url())
    else:
        form = NewMenuForm()

    return render(request, "tillmenu/index.html",
                  context={
                      'menus': menus,
                      'form': form,
                  })

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'contents']
        widgets = {
            'contents': forms.Textarea(
                attrs={
                    'cols': 80, 'rows': 20,
                    'onchange': 'disable_install()',
                    'oninput': 'disable_install()',
                    'onpaste': 'disable_install()',
                }),
        }

def menu(request, menuid):
    try:
        menu = Menu.objects.get(id=int(menuid))
    except Menu.DoesNotExist:
        return Http404

    if request.method == 'POST' and 'save' in request.POST:
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('')
    else:
        form = MenuForm(instance=menu)

    if request.method == 'POST' and 'delete' in request.POST:
        menu.delete()
        return HttpResponseRedirect(reverse('tillmenu-index'))

    parsed = ""
    error = ""
    output = ""
    try:
        parsed = parser.text_to_tree(menu.contents)
        output = parser.output_menu(parsed)
    except parser.ParseError as e:
        error = str(e)

    if output and request.method == 'POST' and 'activate' in request.POST:
        with open('foodmenu.py', 'w') as f:
            f.write(parser.boilerplate)
            f.write(output)
            f.write('\n')
        return HttpResponseRedirect('')
        
    return render(request, "tillmenu/menu.html",
                  context={
                      'menu': menu,
                      'form': form,
                      'parsed': parsed,
                      'output': output,
                      'error': error,
                  })
