#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from ratonator.settings import *

from front.models import *

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseNotFound)
from django.shortcuts import render_to_response,  redirect
from django.template import RequestContext
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

import logging
log = logging.getLogger(__name__)
log.info("Logging started")

CURRENT_LANGUAGE = 'django_language'
RATEABLE_USER = 'rateable_user'


def _current_language(request):
    cl = RATONATOR_DEFAULT_LANGUAGE
    if (CURRENT_LANGUAGE in request.session and
        request.session[CURRENT_LANGUAGE]):
        cl = request.session[CURRENT_LANGUAGE]
    elif (LANGUAGE_COOKIE_NAME in request.COOKIES and
        request.COOKIES[LANGUAGE_COOKIE_NAME]):
        cl = request.session[CURRENT_LANGUAGE] = (
            request.COOKIES[LANGUAGE_COOKIE_NAME])
    return cl


def _general_forms(request):
    (search_form, logon_form) = (
        SearchForm(auto_id="search_form_%s"),
        LogonForm(auto_id="logon_form_%s"))
    return (search_form, logon_form)


def root(request):
    (search_form, logon_form) = _general_forms(request)
    language_choices = Language.list()
    return render_to_response("language_choices.html", locals(),
        context_instance=RequestContext(request))


def index(request,  language_code):
    (search_form, logon_form) = _general_forms(request)
    return _index(request, language_code, search_form, logon_form)
    #Historic response:
    #return HttpResponse("Rate-o-nator (aka Ratonator) up and running!")


def _index(request, language_code, search_form, logon_form):
    if language_code != _current_language(request):
        _activate_language(request,  language_code)
    hot_subjects = ClassifiableRateableStuff.hotSubjects(language_code)
    top_subjects = ClassifiableRateableStuff.topSubjects(language_code)
    new_subjects = ClassifiableRateableStuff.newSubjects(language_code)
    return _set_language(request,  language_code,
        render_to_response("index.html", locals(),
            context_instance=RequestContext(request)))


def addSubject(request):
    (search_form, logon_form) = _general_forms(request)
    if not request.method == 'POST':
        add_subject_form = AddSubjectForm(auto_id="add_subject_form_%s")
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))
    add_subject_form = AddSubjectForm(request.POST,  auto_id="add_subject_form_%s")
    if not add_subject_form.is_valid():
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))
    new_name = add_subject_form.cleaned_data['name']
    try:
        new_subject = ClassifiableRateableStuff.addSubject(new_name, _current_language(request), request.session[RATEABLE_USER])
    except ClassifiableRateableStuff.NotSluggable:
        add_subject_form.errors['name'] = [ _('"%s" is not a valid subject name') % new_name ]
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))
    except ClassifiableRateableStuff.AlreadyExists:
        add_subject_form.errors['name'] = [ _('"%s" already exists') % new_name ]
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))

    return redirect('front.views.subject',  language_code=new_subject.language,  subject_name_slugged=new_subject.nameSlugged)



def addDefinition(request, rateable_uuid):
    subject = ClassifiableRateableStuff.objects.get(uuid=rateable_uuid)
    (search_form, logon_form) = _general_forms(request)
    if not request.method == 'POST':
        add_definition_form = AddDefinitionForm(auto_id="add_definition_form_%s")
        return render_to_response('addDefinition.html', locals(), context_instance=RequestContext(request))
    add_definition_form = AddDefinitionForm(request.POST,  auto_id="add_definition_form_%s")
    if not add_definition_form.is_valid():
        return render_to_response('addDefinition.html', locals(), context_instance=RequestContext(request))

    user = request.session[RATEABLE_USER]

    subject.addDefinition(add_definition_form.cleaned_data['definition'], user)

    return redirect('front.views.subject',  language_code=subject.language,  subject_name_slugged=subject.nameSlugged)



def add_rate_with_parameters(request,  rateable_uuid):
    return add_rate(request,  rateable_uuid)


def add_rate(request,  rateable_uuid):
    (search_form, logon_form) = _general_forms(request)
    subject = RateableStuff.objects.get(uuid=rateable_uuid).downclassed
    rateable_description = subject.description

    if not request.method == 'POST':
        add_rate_form = AddRateForm(auto_id="add_rate_form_%d")
        return render_to_response('addRate.html', locals(), context_instance=RequestContext(request))
    add_rate_form = AddRateForm(request.POST,  auto_id="add_rate_form_%d")
    if not add_rate_form.is_valid():
        return render_to_response('addRate.html', locals(), context_instance=RequestContext(request))

    user = request.session[RATEABLE_USER]

    subject.addRate(add_rate_form.cleaned_data['rate'], add_rate_form.cleaned_data['comments'], user)

    return render_to_response('thickbox_iframe_closer.html',  locals())



def addCategory(request, rateable_uuid):
    try:
        subject = ClassifiableRateableStuff.objects.get(uuid=rateable_uuid)
    except ClassifiableRateableStuff.DoesNotExist:
        return _subject_does_not_exist(request, _current_language(request), rateable_uuid)
    (search_form, logon_form) = _general_forms(request)
    if not request.method == 'POST':
        add_category_form = AddCategoryForm(auto_id="add_category_form_%s")
        return render_to_response('addCategory.html', locals(), context_instance=RequestContext(request))
    add_category_form = AddCategoryForm(request.POST,  auto_id="add_category_form_%s")
    if not add_category_form.is_valid():
        return render_to_response('addCategory.html', locals(), context_instance=RequestContext(request))

    user = request.session[RATEABLE_USER]

    subject.addCategory(add_category_form.cleaned_data['name'], user)

    return redirect('front.views.subject',  language_code=subject.language,  subject_name_slugged=subject.nameSlugged)



# Deprecated, permanent
def subject_old(request,  language_code,  subject_name_slugged):
    return redirect('front.views.subject',  language_code=language_code,  subject_name_slugged=subject_name_slugged,  permanent=True)



def rates(request,  rateable_uuid):
    subject = RateableStuff.objects.get(uuid=rateable_uuid)
    (search_form, logon_form) = _general_forms(request)
    return render_to_response('rates.html',  locals(),  context_instance=RequestContext(request))



def subject(request, language_code, subject_name_slugged):
    re_slugged = i18n_slugify(subject_name_slugged)
    if subject_name_slugged != re_slugged: # provavel url informada pelo usuario
        return _set_language(request,  language_code, redirect('front.views.subject',  language_code=language_code,  subject_name_slugged=re_slugged,  permanent=True))
    if language_code != _current_language(request):
        _activate_language(request,  language_code)
    try:
        subject = ClassifiableRateableStuff.get(language_code, re_slugged)
    except ClassifiableRateableStuff.DoesNotExist:
        return _subject_does_not_exist(request,  language_code, subject_name_slugged)
    (search_form, logon_form) = _general_forms(request)
    (definitions, rates, subjects_above, subjects_below) = subject.sample()
    return _set_language(request,  language_code, render_to_response("subject.html", locals(), context_instance=RequestContext(request)))



def _subject_does_not_exist(request,  language_code,  subject_name_slugged):
    # TODO: Deal with subjects not found - see ambiguator? make a similarity check?
    (search_form, logon_form) = _general_forms(request)
    return HttpResponseNotFound(render_to_response("404.html"))



def search(request):
    # TODO: Search
    return HttpResponse('not implemented yet')



# Deprecated, permanent
def language(request,  language_code):
    return _set_language(request,  language_code,  redirect('front.views.index',  language_code,  permanent=True))



def _activate_language(request,  language_code):
    translation.activate(language_code)
    request.LANGUAGE_CODE = translation.get_language()



# sets language on exit for language based pages
def _set_language(request,  language_code,  response):
    _activate_language(request,  language_code)
    if not CURRENT_LANGUAGE in request.session or request.session[CURRENT_LANGUAGE] != language_code:
        request.session[CURRENT_LANGUAGE] = language_code
    if not response == None:
        if not LANGUAGE_COOKIE_NAME in request.COOKIES or not request.COOKIES[LANGUAGE_COOKIE_NAME] == language_code:
            response.cookies[LANGUAGE_COOKIE_NAME] = language_code
    return response


def logoff(request):
    language = _current_language(request)
    logout(request)
    return redirect('front.views.language',  language_code = language)



def logon(request):
    (search_form, logon_form) = _general_forms(request)

    if not request.method == 'POST':
        return redirect('front.views.root')

    logon_form = LogonForm(request.POST,  auto_id="logon_form_%s")

    if not logon_form.is_valid():
        return _index(request, _current_language(request), search_form, logon_form)

    user = authenticate(username=logon_form.cleaned_data['username'], password=logon_form.cleaned_data['password'])

    if user is None:
        log.info("User '{0}' unable to authenticate".format(logon_form.cleaned_data['username']))
        logon_form.errors['username'] = [ _('Logon failure') ]
        return _index(request, _current_language(request), search_form, logon_form)

    log.info("User '{0}' authenticated".format(user.username))

    try:
        profile = user.get_profile()
    except RateableUser.DoesNotExist:
        log.warn("Logon: User '{0}' not a RateableUser. Logon failure.".format(user.username))
        logon_form.errors['username'] = [ _('Logon failure') ]
        return _index(request, _current_language(request), search_form, logon_form)

    if not user.is_active or profile.validatedAt == None:
        logon_form.errors['username'] = [ _('Inactive account. Please check your email for activation instructions.') ]
        return _index(request, _current_language(request), search_form, logon_form)

    login(request, user)

    rateable_user = user.get_profile()
    request.session[RATEABLE_USER] = rateable_user
    return _set_language(request,  rateable_user.defaultLanguage, redirect('front.views.index',  rateable_user.defaultLanguage))



def user(request,  username):
    (search_form, logon_form) = _general_forms(request)
    try:
        rateable_user = User.objects.get(username=username).get_profile()
    except User.DoesNotExist:
        return HttpResponseNotFound(render_to_response("404.html"))
    contributions = rateable_user.get_contributions()
    return render_to_response('user.html',  locals(),  context_instance=RequestContext(request))



def user_profile(request, scope):
    if request.method != 'POST':
        rateable_user = request.session[RATEABLE_USER]
        user_profile_form = UserProfileForm(auto_id="user_profile_form_%s")
        user_profile_form.fields['preferred_language'].initial = rateable_user.defaultLanguage
        #user_profile_form.fields['email'].initial = rateable_user.user.email
        #user_profile_form.fields['username'].initial = rateable_user.user.username
        password_change_form = PasswordChangeForm(auto_id="password_change_form_%s")
        (search_form, logon_form) = _general_forms(request)
        return render_to_response('user_profile.html',  locals(),  context_instance=RequestContext(request))
    if scope=='Profile':
        return _update_profile(request)
    elif scope=='Password':
        return _update_password(request)
    else:
        raise ValueError,  "Unexpected scope '%s'" % scope



def _update_profile(request):
    user_profile_form = UserProfileForm(request.POST,  auto_id="user_profile_form_%s")
    password_change_form = PasswordChangeForm(auto_id="password_change_form_%s")
    if not user_profile_form.is_valid():
        return render_to_response('user_profile.html',  locals(),  context_instance=RequestContext(request))
    rateable_user = request.session[RATEABLE_USER]
    rateable_user.update_profile(user_profile_form.cleaned_data['preferred_language'])
    title = _('Profile updated')
    messages = [_('Your profile was updated')]
    return render_to_response('messages.html',  locals(),  context_instance=RequestContext(request))



def _update_password(request):
    pass



def register(request):
    (search_form, logon_form) = _general_forms(request)
    if not request.method == 'POST':
        register_form = RegisterForm(auto_id="register_form_%s")
        register_form.fields['preferred_language'].initial = _current_language(request)
        return render_to_response('register.html', locals(), context_instance=RequestContext(request))
    register_form = RegisterForm(request.POST,  auto_id='register_form_%s')
    if not register_form.is_valid():
        return render_to_response('register.html', locals(), context_instance=RequestContext(request))
    if register_form.cleaned_data['password1'] != register_form.cleaned_data['password2']:
        register_form.errors['password2'] = [ _('Passwords do not match') ]
        return render_to_response('register.html', locals(), context_instance=RequestContext(request))
    try:
        RateableUser.register_new_user(
            username=register_form.cleaned_data['username'],
            email=register_form.cleaned_data['email'],
            password1=register_form.cleaned_data['password1'],
            password2=register_form.cleaned_data['password2'],
            preferred_language=register_form.cleaned_data['preferred_language']
        )
    except RateableUser.ValidationException,  ex:
        register_form.errors[ex.property] = ex.messages
        return render_to_response('register.html', locals(), context_instance=RequestContext(request))
    title = _('Account creation in progress')
    messages = [
        _('Your account has been succesfully created.'),
        _('But, before you can start using it, you must validate your email.'),
        _('This step is needed to avoid creation of false accounts.'),
        _('Please, check your email inbox for a message from ratonator.com with further instructions.')
    ]
    return render_to_response('messages.html',  locals(),  context_instance=RequestContext(request))



def registration_validation(request,  key):
    try:
        UserValidation.get(key=key).end_account_validation_process()
        title = _('Be Welcome!')
        messages = [
            _('Welcome to ratonator.com!'),
            _('Your account is now activated!'),
            _('From now on you will be able to:'),
            _('Create new subjects'),
            _('Classify them'),
            _('RATE EVERYTHING!'),
            _('Even rate the ratings!'),
            _('Have fun!!!')
        ]
    except UserValidation.ValidationException,  ex:
        title = _('Account activation error')
        messages = [ ex.message ]
    (search_form, logon_form) = _general_forms(request)
    return render_to_response('messages.html',  locals(),  context_instance=RequestContext(request))



def forgot_password(request):
    (search_form, logon_form) = _general_forms(request)
    if not request.method == 'POST':
        forgot_password_form = ForgotPasswordForm(auto_id='forgot_password_form_%s')
        return render_to_response('forgot_password.html',  locals(),  context_instance=RequestContext(request))
    forgot_password_form = ForgotPasswordForm(request.POST,  auto_id='forgot_password_form_%s')
    if not forgot_password_form.is_valid():
        return render_to_response('forgot_password.html',  locals(),  context_instance=RequestContext(request))
    if not forgot_password_form.cleaned_data['email'] and not forgot_password_form.cleaned_data['username']:
        forgot_password_form.errors['email'] = [
            _('Please, provide your email or your ratonator username') ]
        return render_to_response('forgot_password.html',  locals(),
            context_instance=RequestContext(request))
    try:
        RateableUser.get(
            email = forgot_password_form.cleaned_data['email'],
            username = forgot_password_form.cleaned_data['username']
        ).begin_password_reset_process()
    except RateableUser.Unknown,  e:
        forgot_password_form.errors[e.property_name] = [
            _('Unknown %(what)s "%(value)s"') % {
                'what': e.property_name,
                'value': e.property_value } ]
        return render_to_response('forgot_password.html',  locals(),
            context_instance=RequestContext(request))
    title = _('Password reset email sent')
    messages = [ _('An email was sent to you with instructions for'
        ' reseting your password') ]
    return render_to_response('messages.html',  locals(),
        context_instance=RequestContext(request))



def password_reset(request,  key):
    (search_form, logon_form) = _general_forms(request)
    if not request.method == 'POST':
        password_reset_form = PasswordResetForm(
            auto_id='password_reset_form_%s')
        password_reset_form.fields['key'].initial = key
        return render_to_response('password_reset.html',  locals(),
            context_instance=RequestContext(request))
    password_reset_form = PasswordResetForm(request.POST,
        auto_id='password_reset_form_%s')
    if not password_reset_form.is_valid():
        return render_to_response('password_reset.html',  locals(),
            context_instance=RequestContext(request))
    try:
        PasswordResetRequest.get(key = password_reset_form.cleaned_data['key']
            ).end_password_reset_process(
                password_reset_form.cleaned_data['password1'],
                password_reset_form.cleaned_data['password2'])
    except PasswordResetRequest.ValidationException,  ex:
        password_reset_form.errors[ex.property] = ex.messages
        return render_to_response('password_reset.html',  locals(),
            context_instance=RequestContext(request))
    title = _('Password set')
    messages = [ _('Your new password is ready for use!'),
        _(
            'Please use the logon form in this page to use'
            ' the full capabilites of ratonator.com') ]
    return render_to_response('messages.html',  locals(),
        context_instance=RequestContext(request))



class AddSubjectForm(forms.Form):
    name = forms.CharField(max_length=255, label=_("Name"))
    #definition = forms.CharField(widget=forms.Textarea, label=_("Definition"))
    #categories = forms.CharField(widget=forms.Textarea)
    #rate = forms.ChoiceField(widget=forms.RadioSelect, choices=RATE_CHOICES)
    #rateComment = forms.CharField(widget=forms.Textarea)



class AddDefinitionForm(forms.Form):
    definition = forms.CharField(widget=forms.Textarea, label=_("Definition"))



class AddRateForm(forms.Form):
    rate = forms.ChoiceField(widget=forms.RadioSelect, choices=RATE_CHOICES,
        label=_("Rate"),  initial=5)
    comments = forms.CharField(widget=forms.Textarea, label=_("Comments"))


class AddCategoryForm(forms.Form):
    name = forms.CharField(max_length=255, label=_("Name"))


class LanguageForm(forms.Form):
    language = forms.ChoiceField(label=_("Language"),
        choices=Language.choices())


class LogonForm(forms.Form):
    username = forms.CharField(label=_("User name"), max_length=30)
    password = forms.CharField(label=_("Password"), max_length=32,
        widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    email = forms.EmailField(label=_("email"))
    username = forms.CharField(label=_('Public username'), max_length=30)
    password1 = forms.CharField(label=_('Password'), max_length=32,
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm'), max_length=32,
        widget=forms.PasswordInput)
    preferred_language = forms.ChoiceField(label=_('Preferred language'),
        choices=Language.choices())


class SearchForm(forms.Form):
    pattern = forms.CharField(label=_("Search"), max_length=255)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label=_("email"),  required=False)
    username = forms.CharField(
        label=_('Public username'),
        max_length=30,
        required=False)


class PasswordResetForm(forms.Form):
    key = forms.CharField(widget=forms.HiddenInput)
    password1 = forms.CharField(
        label=_('New Password'),
        max_length=32,
        widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_('Confirm'),
        max_length=32,
        widget=forms.PasswordInput)


class UserProfileForm(forms.Form):
    #email = forms.EmailField(label=_("email"))
    #username = forms.CharField(label=_('Public username'), max_length=30)
    preferred_language = forms.ChoiceField(
        label=_('Preferred language'), choices=Language.choices())


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label=_('Current Password'),
        max_length=32,
        widget=forms.PasswordInput)
    password1 = forms.CharField(
        label=_('New Password'),
        max_length=32,
        widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_('Confirm'),
        max_length=32,
        widget=forms.PasswordInput)
