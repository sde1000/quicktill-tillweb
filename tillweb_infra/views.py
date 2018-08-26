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
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import undefer, defer, undefer_group
from sqlalchemy import distinct
from sqlalchemy import func

import datetime
import django.utils.timezone

class EventInfo:
    def __init__(self, override_time=None):
        # Work out how far through the event we are, based on the current
        # time or on the supplied time.
        self.now = override_time or datetime.datetime.now()

        self.length = datetime.timedelta()
        self.total_consumption = 0.0
        self.time_passed = datetime.timedelta()
        self.expected_consumption = 0.0
        self.open = False
        self.next_open = None
        self.closes_at = None
        for start, end, weight in settings.EVENT_TIMES:
            self.length += (end - start)
            self.total_consumption += weight
            if self.now >= end:
                # This segment has passed.
                self.time_passed += (end - start)
                self.expected_consumption += weight
            elif self.now >= start and self.now < end:
                # We are in this segment.
                self.open = True
                self.closes_at = end
                self.time_passed += (self.now - start)
                self.expected_consumption += weight * (
                    (self.now - start) / (end - start))
            elif self.now < start and not self.next_open:
                self.next_open = start
        self.completed_fraction = self.time_passed / self.length
        self.completed_pct = self.completed_fraction * 100.0
        self.expected_consumption_fraction = self.expected_consumption \
                                             / self.total_consumption
        self.expected_consumption_pct = self.expected_consumption_fraction \
                                        * 100.0

def booziness(s):
    """How much booze have we used?

    Pass in an ORM session.  Returns tuple of amount of alcohol used
    and total amount of alcohol.
    """

    used_fraction = case([(StockItem.finished != None, 1.0)],
                    else_=StockItem.used / StockUnit.size)

    # Amount of alcohol in stock item in ml.  The unit ID we're not listing
    # here is 'ml' which is size 1ml
    unit_alcohol = case([(StockUnit.unit_id == 'pt', 568.0),
                        (StockUnit.unit_id == '25ml', 25.0),
                        (StockUnit.unit_id == '50ml', 50.0),
                        (StockUnit.unit_id == 'can', 350.0),
                        (StockUnit.unit_id == 'bottle', 330.0),
                        ], else_=1.0) * StockUnit.size * StockType.abv / 100.0

    return s.query(func.sum(used_fraction * unit_alcohol),
                    func.sum(unit_alcohol))\
             .select_from(StockItem)\
             .join('stocktype')\
             .join('stockunit')\
             .filter(StockType.abv != None)\
             .one()

def on_tap(s):
    # Used in display_on_tap and frontpage
    base = s.query(StockItem, StockItem.remaining / StockUnit.size)\
            .join('stocktype')\
            .join('stockline')\
            .join('stockunit')\
            .filter(StockLine.location == "Bar")\
            .order_by(StockType.manufacturer, StockType.name)\
            .options(undefer('remaining'))\
            .options(contains_eager('stocktype'))

    ales = base.filter(StockType.dept_id == 1).all()

    kegs = base.filter(StockType.dept_id.in_([2, 13])).all()

    ciders = base.filter(StockType.dept_id == 3).all()

    return ales, kegs, ciders

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

# We use this date format in templates - defined here so we don't have
# to keep repeating it.  It's available in templates as 'dtf'
dtf = "Y-m-d H:i"

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
    ales, kegs, ciders = on_tap(s)

    return render(request, 'display-on-tap.html',
                  context={'ales': ales, 'kegs': kegs, 'ciders': ciders})

def display_cans_and_bottles(request):
    s = settings.TILLWEB_DATABASE()
    # We want all stocktypes with unit 'can' or unit 'bottle', but only
    # if there are >0 qty remaining
    r = s.query(StockType)\
        .filter(StockType.unit_id.in_(['can', 'bottle']))\
        .filter(StockType.remaining > 0.0)\
        .filter(StockType.abv != None)\
        .options(undefer('remaining'))\
        .order_by(StockType.manufacturer, StockType.name)\
        .all()

    return render(request, 'display-cans-and-bottles.html',
                  context={'types': r})

def display_progress(request):
    s = settings.TILLWEB_DATABASE()
    alcohol_used, total_alcohol = booziness(s)
    info = EventInfo()

    return render(request, 'display-progress.html',
                  context={
                      'info': info, 'alcohol_used': alcohol_used,
                      'total_alcohol': total_alcohol,
                      'alcohol_used_pct': alcohol_used / total_alcohol * 100.0})

def frontpage(request):
    s = settings.TILLWEB_DATABASE()

    # Testing:
    info = EventInfo(datetime.datetime(2018, 9, 1, 11, 30))
    # Production:
    #info = EventInfo()

    alcohol_used, total_alcohol = booziness(s)

    ales, kegs, ciders = on_tap(s)

    return render(request, "whatson.html",
                  {"info": info,
                   "alcohol_used": alcohol_used,
                   "total_alcohol": total_alcohol,
                   "alcohol_used_pct": (alcohol_used / total_alcohol) * 100.0,
                   "ales": ales,
                   "kegs": kegs,
                   "ciders": ciders,
                  })

def locations_json(request):
    s = settings.TILLWEB_DATABASE()
    locations = [x[0] for x in s.query(distinct(StockLine.location))
                 .order_by(StockLine.location).all()]
    return JsonResponse({'locations': locations})

def location_json(request, location):
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

def stock_json(request):
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

def progress_json(request):
    s = settings.TILLWEB_DATABASE()
    alcohol_used, total_alcohol = booziness(s)
    info = EventInfo()

    return JsonResponse(
        {'licensed_time_pct': info.completed_pct,
         'expected_consumption_pct': info.expected_consumption_pct,
         'actual_consumption_pct': (alcohol_used / total_alcohol) * 100.0,
        })
