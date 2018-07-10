from django.http import HttpResponse, Http404, HttpResponseRedirect
from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Permission
from django.db import IntegrityError
from django.contrib import messages

# They moved it again!  As of django-1.10 reverse is found in
# django.urls, but we need to retain compatibility with django-1.8
# while we are still targetting Ubuntu-16.04 LTS.
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

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
    u = User.objects.all()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = User.objects.create_user(
                    cd['username'],
                    password=cd['newpassword'] if cd['newpassword'] else None)
                if not cd['newpassword']:
                    messages.warning(request, "New user has no password set "
                                     "and will not be able to log in")
                user.first_name = cd['firstname']
                user.last_name = cd['lastname']
                if cd['privileged']:
                    permission = Permission.objects.get(codename="add_user")
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
        u = User.objects.get(id=int(userid))
    except User.DoesNotExist:
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
                    permission = Permission.objects.get(codename="add_user")
                    u.user_permissions.add(permission)
                if not cd['privileged'] and u.has_perm("auth.add_user"):
                    permission = Permission.objects.get(codename="add_user")
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
