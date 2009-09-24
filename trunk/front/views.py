#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import settings
from front.models import *
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response,  redirect
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

CURRENT_LANGUAGE = 'django_language'
RATEABLE_USER = 'rateable_user'

def __general_forms(request):
    (language_form, search_form, logon_form) = (LanguageForm(), SearchForm(), LogonForm())
    if not CURRENT_LANGUAGE in request.session:
        request.session[CURRENT_LANGUAGE] = settings.RATONATOR_DEFAULT_LANGUAGE
    language_form.fields['language'].initial = request.session[CURRENT_LANGUAGE]
    return (language_form, search_form, logon_form)



def index(request):
    (language_form, search_form, logon_form) = __general_forms(request)
    return __index(request, language_form, search_form, logon_form)
    #Historic response:
    #return HttpResponse("Rate-o-nator (aka Ratonator) up and running!")



def __index(request, language_form, search_form, logon_form):
    hot_subjects = ClassifiableRateableStuff.hotSubjects(request.session[CURRENT_LANGUAGE])
    top_subjects = ClassifiableRateableStuff.topSubjects(request.session[CURRENT_LANGUAGE])
    new_subjects = ClassifiableRateableStuff.newSubjects(request.session[CURRENT_LANGUAGE])
    return render_to_response("index.html", locals(), context_instance=RequestContext(request))



def addSubject(request):
    (language_form, search_form, logon_form) = __general_forms(request)
    if not request.method == 'POST':
        add_subject_form = AddSubjectForm()
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))
    add_subject_form = AddSubjectForm(request.POST)
    if not add_subject_form.is_valid():
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))

    new_name = add_subject_form.cleaned_data['name']

    try:
        new_subject = ClassifiableRateableStuff.addSubject(new_name, request.session[CURRENT_LANGUAGE], request.session[RATEABLE_USER], add_subject_form.cleaned_data['definition'])
    except ClassifiableRateableStuff.NotSluggable:
        add_subject_form.errors['name'] = [ _('"%s" is not a valid subject name') % new_name ]
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))
    except ClassifiableRateableStuff.AlreadyExists:
        add_subject_form.errors['name'] = [ _('"%s" already exists') % new_name ]
        return render_to_response('addSubject.html', locals(), context_instance=RequestContext(request))

    return redirect('front.views.subject',  language_code=new_subject.language,  subject_name_slugged=new_subject.nameSlugged)



def addDefinition(request, language_code, subject_name_slugged):
    subject = ClassifiableRateableStuff.get(language_code, subject_name_slugged)
    (language_form, search_form, logon_form) = __general_forms(request)
    if not request.method == 'POST':
        add_definition_form = AddDefinitionForm()
        return render_to_response('addDefinition.html', locals(), context_instance=RequestContext(request))
    add_definition_form = AddDefinitionForm(request.POST)
    if not add_definition_form.is_valid():
        return render_to_response('addDefinition.html', locals(), context_instance=RequestContext(request))

    user = request.session[RATEABLE_USER]

    subject.addDefinition(add_definition_form.cleaned_data['definition'], user)

    return redirect('front.views.subject',  language_code=subject.language,  subject_name_slugged=subject.nameSlugged)



def addRate(request, language_code, subject_name_slugged):
    try:
        subject = ClassifiableRateableStuff.get(language_code, subject_name_slugged)
    except ClassifiableRateableStuff.DoesNotExist:
        return __subject_does_not_exist(request, language_code, subject_name_slugged)
    return add_rate(request,  'classifiable',  subject.uuid)



def add_rate_with_parameters(request,  rateable_class,  rateable_uuid):
    return add_rate(request,  rateable_class,  rateable_uuid)


RATEABLE_CLASSES = [ 'classifiable',  'rate',  'classification',  'definition',  'user' ]
def add_rate(request,  rateable_class,  rateable_uuid):
    (language_form, search_form, logon_form) = __general_forms(request)
    if rateable_class not in RATEABLE_CLASSES:
        return HttpResponse('Bad request!')
    subject = None
    # TODO: Move this logic to RateableStuff.AddRate()
    if rateable_class == 'classifiable':
        subject = ClassifiableRateableStuff.objects.get(uuid=rateable_uuid)
    if rateable_class == 'rate':
        subject = Rate.objects.get(uuid=rateable_uuid)

    print 'desc 1'
    rateable_description = subject.description
    print 'desc 2 ',  rateable_description

    if not request.method == 'POST':
        add_rate_form = AddRateForm()
        return render_to_response('addRate.html', locals(), context_instance=RequestContext(request))
    add_rate_form = AddRateForm(request.POST)
    if not add_rate_form.is_valid():
        return render_to_response('addRate.html', locals(), context_instance=RequestContext(request))

    user = request.session[RATEABLE_USER]

    subject.addRate(add_rate_form.cleaned_data['rate'], add_rate_form.cleaned_data['comments'], user)

    return render_to_response('thickbox_iframe_closer.html',  locals())
    #return redirect('front.views.subject',  language_code=subject.language,  subject_name_slugged=subject.nameSlugged)



def addCategory(request, language_code, subject_name_slugged):
    try:
        subject = ClassifiableRateableStuff.get(language_code, subject_name_slugged)
    except ClassifiableRateableStuff.DoesNotExist:
        return __subject_does_not_exist(request, language_code, subject_name_slugged)
    (language_form, search_form, logon_form) = __general_forms(request)
    if not request.method == 'POST':
        add_category_form = AddCategoryForm()
        return render_to_response('addCategory.html', locals(), context_instance=RequestContext(request))
    add_category_form = AddCategoryForm(request.POST)
    if not add_category_form.is_valid():
        return render_to_response('addCategory.html', locals(), context_instance=RequestContext(request))

    user = request.session[RATEABLE_USER]

    subject.addCategory(add_category_form.cleaned_data['name'], user)

    return redirect('front.views.subject',  language_code=subject.language,  subject_name_slugged=subject.nameSlugged)



def subject(request, language_code, subject_name_slugged):
    try:
        subject = ClassifiableRateableStuff.get(language_code, subject_name_slugged)
        if subject.nameSlugged != subject_name_slugged:
            return redirect('front.views.subject',  language_code=subject.language,  subject_name_slugged=subject.nameSlugged)
    except ClassifiableRateableStuff.DoesNotExist:
        return __subject_does_not_exist(request,  language_code, subject_name_slugged)
    (language_form, search_form, logon_form) = __general_forms(request)
    (definitions, rates, subjects_above, subjects_below) = subject.sample()
    return render_to_response("subject.html", locals(), context_instance=RequestContext(request))



def __subject_does_not_exist(request,  language_code,  subject_name_slugged):
    # TODO: Deal with subjects not found - see ambiguator? make a similarity check?
    pass



def search(request):
    # TODO: Search
    return HttpResponse('not implemented yet')



def language(request,  language_code):
    request.session[CURRENT_LANGUAGE] = language_code

    return redirect('front.views.index')



def logoff(request):
    logout(request)
    return redirect('front.views.index')



def logon(request):
    (language_form, search_form, logon_form) = __general_forms(request)
    referer = request.META['HTTP_REFERER'] or '/'

    if not request.method == 'POST':
        return HttpResponseRedirect(referer)

    logon_form = LogonForm(request.POST)

    if not logon_form.is_valid():
        return __index(request, language_form, search_form, logon_form)

    user = authenticate(username=logon_form.cleaned_data['username'], password=logon_form.cleaned_data['password'])

    if user is None:
        logon_form.errors['username'] = [ _('Logon failure') ]
        return __index(request, language_form, search_form, logon_form)

    if not user.is_active:
        logon_form.errors['username'] = [ _('Inactive account') ]
        return __index(request, language_form, search_form, logon_form)

    login(request, user)

    rateable_user = user.get_profile()
    request.session[RATEABLE_USER] = rateable_user
    request.session[CURRENT_LANGUAGE] = rateable_user.defaultLanguage
    return HttpResponseRedirect(referer)



def register(request):
    if not request.method == POST:
        (language_form, search_form, logon_form) = __general_forms(request)
        add_subject_form = RegisterForm()
        return render_to_response('register.html', locals(), context_instance=RequestContext(request))
    else:
        pass



class AddSubjectForm(forms.Form):
    name = forms.CharField(max_length=255, label=_("Name"))
    definition = forms.CharField(widget=forms.Textarea, label=_("Definition"))
    #categories = forms.CharField(widget=forms.Textarea)
    #rate = forms.ChoiceField(widget=forms.RadioSelect, choices=RATE_CHOICES)
    #rateComment = forms.CharField(widget=forms.Textarea)



class AddDefinitionForm(forms.Form):
    definition = forms.CharField(widget=forms.Textarea, label=_("Definition"))



class AddRateForm(forms.Form):
    rate = forms.ChoiceField(widget=forms.RadioSelect, choices=RATE_CHOICES, label=_("Rate"))
    comments = forms.CharField(widget=forms.Textarea, label=_("Comments"))



class AddCategoryForm(forms.Form):
    name = forms.CharField(max_length=255, label=_("Name"))



class LanguageForm(forms.Form):
    language = forms.ChoiceField(label=_("Language"), choices=Language.choices())



class LogonForm(forms.Form):
    remember_me = forms.BooleanField(label=_('Remember me'), initial=False, required=False)
    username = forms.CharField(label=_("User name"), max_length=30)
    password = forms.CharField(label=_("Password"), max_length=32, widget=forms.PasswordInput)



class RegisterForm(forms.Form):
    email = forms.EmailField(label=_("email"))
    username = forms.CharField(label=_('Public username'), max_length=30)
    password1 = forms.CharField(label=_('Password'), max_length=32, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm'), max_length=32, widget=forms.PasswordInput)
    preferred_language = forms.ChoiceField(label=_('Preferred language'),  choices=Language.choices())



class SearchForm(forms.Form):
    pattern = forms.CharField(label=_("Search"), max_length=255)

