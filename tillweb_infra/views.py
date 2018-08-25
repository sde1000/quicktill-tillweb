from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.http import JsonResponse
from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User as authUser
from django.contrib.auth.models import Permission as authPermission
from django.db import IntegrityError
from django.contrib import messages
from django.conf import settings

from django.urls import reverse

from quicktill.version import version

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import subqueryload, subqueryload_all
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.orm import lazyload
from sqlalchemy.orm import defaultload
from sqlalchemy.orm import undefer, defer, undefer_group
from sqlalchemy import distinct

def index(request):
    return render(request, "index.html", {'pubname': settings.TILLWEB_PUBNAME})

@login_required
def userprofile(request):
    may_edit_users = request.user.has_perm("auth.add_user")
    return render(request, "registration/profile.html",
                  {'may_edit_users': may_edit_users})

class PasswordChangeForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput,
                               label="Current password")
    newpassword = forms.CharField(widget=forms.PasswordInput,
                                  label="New password",
                                  min_length=7, max_length=80)
    passwordagain = forms.CharField(widget=forms.PasswordInput,
                                    label="New password again",
                                    min_length=7, max_length=80)

    def clean(self):
        try:
            if self.cleaned_data['newpassword'] \
               != self.cleaned_data['passwordagain']:
                raise forms.ValidationError(
                    "You must enter the same new password in both fields")
        except KeyError:
            pass
        return self.cleaned_data

@login_required
def pwchange(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if request.user.check_password(cd['password']):
                request.user.set_password(cd['newpassword'])
                request.user.save()
                messages.info(request,"Password changed")
                return HttpResponseRedirect(
                    reverse("user-profile-page"))
            else:
                messages.info(request,"Incorrect password - changes not made")
            return HttpResponseRedirect("")
    else:
        form = PasswordChangeForm()
    return render(request, 'registration/password-change.html',
                  context={'form': form})

class UserForm(forms.Form):
    username = forms.CharField(label="Username")
    firstname = forms.CharField(label="First name")
    lastname = forms.CharField(label="Last name")
    newpassword = forms.CharField(widget=forms.PasswordInput,
                                  label="New password",
                                  min_length=7, max_length=80,
                                  required=False)
    passwordagain = forms.CharField(widget=forms.PasswordInput,
                                    label="New password again",
                                    min_length=7, max_length=80,
                                    required=False)
    privileged = forms.BooleanField(
        label="Tick if user may add/edit other users",
        required=False)

    def clean(self):
        try:
            if self.cleaned_data['newpassword'] \
               != self.cleaned_data['passwordagain']:
                raise forms.ValidationError(
                    "You must enter the same new password in both fields")
        except KeyError:
            pass
        return self.cleaned_data

@permission_required("auth.add_user")
def users(request):
    u = authUser.objects.all()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = authUser.objects.create_user(
                    cd['username'],
                    password=cd['newpassword'] if cd['newpassword'] else None)
                if not cd['newpassword']:
                    messages.warning(request, "New user has no password set "
                                     "and will not be able to log in")
                user.first_name = cd['firstname']
                user.last_name = cd['lastname']
                if cd['privileged']:
                    permission = authPermission.objects.get(codename="add_user")
                    user.user_permissions.add(permission)
                user.save()
                messages.info(
                    request, "Added new user '{}'".format(cd['username']))
                return HttpResponseRedirect("")
            except IntegrityError:
                form.add_error(None, "That username is already in use")
    else:
        form = UserForm()

    return render(request, 'registration/userlist.html',
                  {'users': u, 'form': form})

@permission_required("auth.add_user")
def userdetail(request, userid):
    try:
        u = authUser.objects.get(id=int(userid))
    except authUser.DoesNotExist:
        raise Http404

    if request.method == 'POST' and (u.is_staff or u.is_superuser):
        messages.error(request, "You cannot edit users marked as 'staff' "
                       "or 'superuser' here; you must use the admin interface "
                       "instead")
        return HttpResponseRedirect("")

    if request.method == 'POST' and 'update' in request.POST:
        form = UserForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['newpassword'] and u == request.user:
                messages.info(request, "You can't change your own password "
                              "here; use the password change page instead")
                return HttpResponseRedirect("")
            try:
                if cd['username'] != u.username:
                    u.username = cd['username']
                if cd['firstname'] != u.first_name:
                    u.first_name = cd['firstname']
                if cd['lastname'] != u.last_name:
                    u.last_name = cd['lastname']
                if cd['newpassword']:
                    u.set_password(cd['newpassword'])
                if cd['privileged'] and not u.has_perm("auth.add_user"):
                    permission = authPermission.objects.get(codename="add_user")
                    u.user_permissions.add(permission)
                if not cd['privileged'] and u.has_perm("auth.add_user"):
                    permission = authPermission.objects.get(codename="add_user")
                    u.user_permissions.remove(permission)
                u.save()
                messages.info(request, "User details updated")
                return HttpResponseRedirect("")
            except IntegrityError:
                form.add_error("username", "That username is already in use")
    elif request.method == 'POST' and 'delete' in request.POST:
        if u == request.user:
            messages.error(request, "You cannot delete yourself")
            return HttpResponseRedirect("")
        u.delete()
        messages.info(request, "User '{}' removed".format(u.username))
        return HttpResponseRedirect(reverse("userlist"))
    else:
        form = UserForm(initial={
            'username': u.username,
            'firstname': u.first_name,
            'lastname': u.last_name,
            'privileged': u.has_perm('auth.add_user'),
        })

    return render(request, 'registration/userdetail.html',
                  {'object': u, 'form': form})

from quicktill.models import *

# XXX HACK

# This is a copy of tillweb_view from quicktill.tillweb.views but with
# the login_required code removed.  This lets us apply @login_required
# on a view-by-view basis.

# We use this date format in templates - defined here so we don't have
# to keep repeating it.  It's available in templates as 'dtf'
dtf = "Y-m-d H:i"

def tillweb_view(view):
    def new_view(request, pubname="", *args, **kwargs):
        till = None
        tillname = settings.TILLWEB_PUBNAME
        access = settings.TILLWEB_DEFAULT_ACCESS
        session = settings.TILLWEB_DATABASE()
        try:
            info = {
                'access': access,
                'tillname': tillname, # Formatted for people
                'pubname': pubname, # Used in url
            }
            result = view(request, info, session, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            t, d = result
            # object is the Till object, possibly used for a nav menu
            # (it's None if we are set up for a single site)
            # till is the name of the till
            # access is 'R','M','F'
            defaults = {'object': till,
                        'till': tillname, 'access': access,
                        'dtf': dtf, 'pubname': pubname,
                        'version': version}
            if t.endswith(".ajax"):
                # AJAX content typically is not a fully-formed HTML document.
                # If requested in a non-AJAX context, add a HTML container.
                if not request.is_ajax():
                    defaults['ajax_content'] = 'tillweb/' + t
                    t = 'non-ajax-container.html'
            defaults.update(d)
            return render(request, 'tillweb/' + t, defaults)
        except OperationalError as oe:
            t = get_template('tillweb/operationalerror.html')
            return HttpResponse(
                t.render(RequestContext(
                        request, {'object':till, 'access':access, 'error':oe})),
                status=503)
        finally:
            session.close()
    return new_view

@login_required
def refusals(request):
    s = settings.TILLWEB_DATABASE()
    r = s.query(RefusalsLog)\
         .options(joinedload('user'))\
         .order_by(RefusalsLog.id)\
         .all()
    return render(request, 'refusals.html',
                  context={'refusals': r,
                           'dtf': dtf,
                  })

def display_on_tap(request):
    s = settings.TILLWEB_DATABASE()
    # We want everything in location "Bar"
    r = s.query(StockLine)\
         .filter(StockLine.location == "Bar")\
         .order_by(StockLine.name)\
         .all()

    return render(request, 'display_on_tap.html',
                  context={'lines': r})

def frontpage(request):
    s = settings.TILLWEB_DATABASE()
    pub = settings.TILLWEB_PUBNAME
    lines = s.query(StockLine)\
             .order_by(StockLine.name)\
             .all()

    stock = s.query(StockType)\
            .filter(StockType.remaining > 0)\
            .order_by(StockType.dept_id)\
            .order_by(StockType.manufacturer)\
            .order_by(StockType.name)\
            .all()
            
    return render(request, "whatson.html",
                  {"pubname": pub,
                   "lines": [
                       (l.name, l.sale_stocktype.format(),
                        l.sale_stocktype.pricestr)
                       for l in lines
                       if l.stockonsale or l.linetype == 'continuous'],
                   "stock": [(s.format(), s.remaining, s.unit.name)
                             for s in stock],
                  })

def locations(request):
    s = settings.TILLWEB_DATABASE()
    locations = [x[0] for x in s.query(distinct(StockLine.location))
                 .order_by(StockLine.location).all()]
    return JsonResponse({'locations': locations})

def location(request, location):
    s = settings.TILLWEB_DATABASE()
    lines = s.query(StockLine)\
             .filter(StockLine.location == location)\
             .order_by(StockLine.name)\
             .all()

    return JsonResponse({'location': [
        {"line": l.name,
         "description": l.sale_stocktype.format(),
         "price": l.sale_stocktype.saleprice,
         "price_for_units": l.sale_stocktype.saleprice_units,
         "unit": l.sale_stocktype.unit.name}
        for l in lines if l.stockonsale or l.linetype == "continuous"]})

def stock(request):
    s = settings.TILLWEB_DATABASE()
    stock = s.query(StockType)\
             .filter(StockType.remaining > 0)\
             .order_by(StockType.dept_id)\
             .order_by(StockType.manufacturer)\
             .order_by(StockType.name)\
             .all()
    return JsonResponse({'stock': [{
        'description': s.format(),
        'remaining': s.remaining,
        'unit': s.unit.name
        } for s in stock]})
