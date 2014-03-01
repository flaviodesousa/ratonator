#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Sum, Avg, Count
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

import datetime
import re
import unicodedata
import uuid
import logging

from ratonator.settings import *

log = logging.getLogger(__name__)
log.info("Logging started")

RATE_CHOICES = (
    (10, _('Impossibly good')),
    (9, _('Best ever')),
    (8, _('Excellent')),
    (7, _('Very good')),
    (6, _('Good')),
    (5, _('Regular')),
    (4, _('Weak')),
    (3, _('Bad')),
    (2, _('Very Bad')),
    (1, _('Worse ever')),
    (0, _('Impossibly bad'))
)

# letters and digits (numbers) - assumed previously lowercased
__I18N_SLUGIFY_ASIS = re.compile('^[LN]')
# punctuations, markers, symbols and separators
__I18N_SLUGIFY_DASH = re.compile('^[PMSZ]')
# removes what is not letters/spaces/dashes
__I18N_SLUGIFY_TONULL = re.compile(u'[^\w\s-]', re.UNICODE)
# converts contiguous spaces and dashes into a single dash
__I18N_SLUGIFY_TODASH = re.compile(u'[-\s_]+', re.UNICODE)


def i18n_slugify(value):
    slugged = u''
    dash = False
    for c in value.strip().lower():
        cat = unicodedata.category(c)
        if __I18N_SLUGIFY_ASIS.match(cat):
            if dash and slugged:
                slugged += '-'
            slugged += c
            dash = False
        elif not dash and __I18N_SLUGIFY_DASH.match(cat):
            dash = True
    return slugged


def unicode_slugify(value):
    #Ongoing try to slugify unicode...
    v = unicodedata.normalize('NFKD', value).encode('utf-8', 'ignore')
    #print u'1 - "%s"' % v
    v = __I18N_SLUGIFY_TONULL.sub(v, '').strip().lower()
    #print u'2 - "%s"' % v
    v = __I18N_SLUGIFY_TODASH.sub(v, '-')
    #print u'3 - "%s"' % v
    return v


def uuidMaker():
    return str(uuid.uuid4())


class Language(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=64, unique=True)
    nativeName = models.CharField(max_length=64, unique=True)

    @classmethod
    def choices(cls):
        return [(l.code, l.nativeName)
            for l in cls.list()]

    @classmethod
    def list(cls):
        return Language.objects.all().order_by('nativeName')


class RateableStuff(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    lastTouchedAt = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey('RateableUser',
        related_name='additions', null=True)
    uuid = models.CharField(max_length=36, unique=True, default=uuidMaker)

    def addRate(self, rate_value, comments_text, user):
        log.info("Adding new rate to {0}".format(uuid))
        try:
            existing = self.rates.filter(createdBy=user).get(
                superseder__isnull=True)
        except Rate.DoesNotExist:
            existing = None
        rate = Rate(
            theRate=rate_value,
            comments=comments_text,
            subject=self,
            createdBy=user)
        rate.save()
        if not existing == None:
            existing.superseder = rate
            existing.save()
        self.touch()
        return self

    def touch(self):
        self.lastTouchedAt = datetime.datetime.now()
        self.save()
        return self

    def __unicode__(self):
        return (
            'RateableStuff{createdAt="%s",'
            'lastTouchedAt="%s",uuid="%s",createdBy=[%s]}' % (
            self.createdAt, self.lastTouchedAt, self.uuid, self.createdBy))

    def getSample(self, max_definitions=5, max_rates=5):
        rates = self.rates.filter(
            superseder__isnull=True).order_by('-createdAt')[:max_rates]
        return rates

    def __aggregates(self):
        try:
            return self.__aggregate_cache
        except AttributeError:
            self.__aggregate_cache = (
                self.rates.filter(superseder__isnull=True)
                .aggregate(Avg('theRate'), Count('theRate')))
            return self.__aggregate_cache

    def get_average_rate(self):
        average = self.__aggregates()['theRate__avg']
        return round(average, 1) if average else None
    average_rate = property(get_average_rate)

    def get_rate_count(self):
        return self.__aggregates()['theRate__count']
    rate_count = property(get_rate_count)

    # TODO: This is ugly!
    # Find another way to find the correct downclassed object on relationships
    def __downclassed(self):
        try:
            return self.__downclassed_cache
        except AttributeError:
            for c in [ClassifiableRateableStuff, Rate, Definition,
                RateableUser, Classification, AspectRate, Aspect, UserBio]:
                try:
                    self.__downclassed_cache = (c.__class__.__name__,
                        c.objects.get(id=self.id))
                    break
                except c.DoesNotExist:
                    continue
            else:
                self.__downclassed_cache = ('unknown',  self)
        return self.__downclassed_cache

    def get_downclassed(self):
        return self.__downclassed()[1]
    downclassed = property(get_downclassed)

    def get_kind(self):
        return self.__downclassed()[0]
    kind = property(get_kind)

    def get_description(self):
        if self.downclassed == self:
            return "unknown id=%d" % self.id
        else:
            return self.downclassed.description
    description = property(get_description)


class Rate(RateableStuff):
    theRate = models.SmallIntegerField()
    comments = models.TextField(null=True)
    superseder = models.OneToOneField('Rate',
        related_name='superseded', null=True)
    subject = models.ForeignKey('RateableStuff', related_name='rates')

    def get_description(self):
        return _("a rate of %(rate)d given by %(user)s to %(subject)s") % {
            'rate': self.theRate,
            'user': self.createdBy.user.username,
            'subject': self.subject.downclassed.description
        }
    description = property(get_description)

    def __unicode__(self):
        return (
            'Rate{theRate="%d",comments="%s",'
            'superseder=[%s],subject=[%s],super=[%s]}' % (
                self.theRate,
                self.comments,
                self.superseder,
                self.subject,
                RateableStuff.__unicode__(self)))


class NameableRateableStuff(RateableStuff):
    name = models.CharField(max_length=255)
    nameSlugged = models.SlugField(max_length=255)
    language = models.CharField(max_length=2)
    disambiguator = models.ForeignKey('Disambiguator',
        related_name='ambiguousSubjects', null=True)

    def get_description(self):
        return _("Unqualified named \"%s\"") % self.name
    description = property(get_description)

    def __unicode__(self):
        return (
            'NameableRateableStuff{name="%s",'
            'nameSlugged="%s",language="%s",super=[%s]}' % (
                self.name,
                self.nameSlugged,
                self.language,
                RateableStuff.__unicode__(self)))

    class Meta:
        unique_together = (
            ("language", "name"),
            ("language", "nameSlugged"),)


class Aspect(NameableRateableStuff):
    subjects = models.ManyToManyField('ClassifiableRateableStuff',
        related_name='aspects')

    def get_description(self):
        return _('Aspect named "%s"') % self.name
    description = property(get_description)


class AspectRate(Rate):
    aspect = models.ForeignKey('Aspect')
    baseRate = models.ForeignKey('Rate', related_name='ratingAspects')

    def get_description(self):
        return _(
            'a rate of %(rate)d given by %(user)s for the '
            '"%(aspect_name)s" aspect of "%(subject_name)s"') % {
                'rate': self.theRate,
                'user': self.createdBy.user.username,
                'aspect_name': self.aspect.name,
                'subject_name': self.subject.description}
    description = property(get_description)


class ClassifiableRateableStuff(NameableRateableStuff):

    class NotSluggable():
        pass

    class AlreadyExists():
        pass

    @classmethod
    def get(cls, language_filter, name_slugged):
        return ClassifiableRateableStuff.objects.filter(
            language=language_filter).get(nameSlugged=name_slugged)

    @classmethod
    def hotSubjects(cls, language_filter, days=30,  page=1,  max_subjects=20):
        sampling_start = datetime.datetime.now() + datetime.timedelta(
            days=-days)
        slice = (page - 1) * max_subjects
        return ClassifiableRateableStuff.objects.filter(
            language=language_filter).filter(
            lastTouchedAt__gte=sampling_start).filter(
            rates__superseder__isnull=True).annotate(
            hotness=Sum('rates__theRate')).filter(
            hotness__isnull=False).order_by('-hotness')

    @classmethod
    def newSubjects(cls, language_filter, page=1,  max_subjects=100):
        slice = (page - 1) * max_subjects
        return ClassifiableRateableStuff.objects.filter(
            language=language_filter).order_by(
            '-createdAt')[slice:max_subjects]

    @classmethod
    def topSubjects(cls,  language_filter, page=1, max_subjects=100):
        slice = (page - 1) * max_subjects
        return ClassifiableRateableStuff.objects.filter(
            language=language_filter).filter(
            rates__superseder__isnull=True).annotate(
            topness=Avg('rates__theRate')).filter(
            topness__isnull=False).order_by('-topness')[slice:max_subjects]

    @classmethod
    def addSubject(cls, name, language, user, definition=None):
        log.info("User '{2}' is creating new ({1}) subject: '{0}'"
            .format(name, language, user.user.username))
        slugged = i18n_slugify(name)
        if not slugged:
            log.warn("Subject '{0}' not sluggable".format(name))
            raise ClassifiableRateableStuff.NotSluggable()
        try:
            ClassifiableRateableStuff.get(language, slugged)
            raise ClassifiableRateableStuff.AlreadyExists()
        except ClassifiableRateableStuff.DoesNotExist:
            pass
        new_subject = ClassifiableRateableStuff()
        new_subject.name = name
        new_subject.nameSlugged = slugged
        new_subject.language = language
        new_subject.createdBy = user
        new_subject.save()
        if definition != None:
            new_subject.addDefinition(definition, user)
        return new_subject

    def get_description(self):
        return self.name
    description = property(get_description)

    def sample(self, max_definitions=5, max_rates=5):
        rates = NameableRateableStuff.getSample(self, max_rates)
        definitions = self.definitions.order_by(
            '-createdAt')[:max_definitions]
        subjects_above = [above for above in self.categories.all()]
        subjects_below = [below for below in self.subjects.all()]
        return (definitions, rates, subjects_above, subjects_below)

    def addDefinition(self, definition_text, user):
        log.info("User '{0}' is adding ('{2}') definition to subject '{1}'"
            .format(user.user.username, self.name, self.language))
        definition = Definition(
            theDefinition=definition_text,
            subject=self,
            createdBy=user)
        definition.save()
        self.touch()
        return self

    def addCategory(self, category_name, user):
        log.info("User '{0}' is adding new category '{1}'"
            .format(user.user.username, category_name))
        try:
            category_name_slugged = i18n_slugify(category_name)
            adding_category = ClassifiableRateableStuff.get(
                self.language,
                category_name_slugged)
        except ClassifiableRateableStuff.DoesNotExist:
            adding_category = ClassifiableRateableStuff.addSubject(
                category_name, self.language, user)
        try:
            existing_classification = Classification.objects.filter(
                category=adding_category).get(subject=self)
        except Classification.DoesNotExist:
            classification = Classification(
                subject=self,
                category=adding_category,
                createdBy=user)
            classification.save()
            self.touch()
        return self

    def __unicode__(self):
        return ("ClassifiableRateableStuff{super=[%s]}"
            % NameableRateableStuff.__unicode__(self))


class Classification(RateableStuff):
    subject = models.ForeignKey('ClassifiableRateableStuff',
        related_name='categories')
    category = models.ForeignKey('ClassifiableRateableStuff',
        related_name='subjects')

    def get_description(self):
        return (_('Classification of "%(subject)s" as a "%(category)s"')
            % {'subject': self.subject.name,  'category': self.category.name})
    description = property(get_description)

    def get_marker(self):
        return 'classification'
    marker = property(get_marker)

    class Meta:
        unique_together = (('subject', 'category'),)


class Definition(RateableStuff):
    theDefinition = models.TextField()
    subject = models.ForeignKey('ClassifiableRateableStuff',
        related_name='definitions')

    def get_description(self):
        return _('Definition of "%(subject)s" as "%(definition)s"') % {
            'subject': self.subject.name,
            'definition': self.theDefinition}
    description = property(get_description)


class Disambiguator(models.Model):
    commonTerm = models.CharField(max_length=255)
    language = models.CharField(max_length=2)

    def __unicode__(self):
        return 'Disambiguator{commonTerm="%s",language="%s"}' % (
            commonTerm, language)

    class Meta:
        unique_together = ('commonTerm', 'language')


class Kill(models.Model):
    killedAt = models.DateTimeField(auto_now_add=True)
    killer = models.ForeignKey('RateableUser', related_name='kills')
    killed = models.ForeignKey('RateableUser', related_name='killers')


class RateableUser(RateableStuff):
    defaultLanguage = models.CharField(max_length=2)
    validatedAt = models.DateTimeField(null=True)
    lastLoggedOnAt = models.DateTimeField(null=True)
    user = models.ForeignKey(User, unique=True)
    # TODO: Add support to user profile (language, rated content, picture)

    def get_description(self):
        return _('user "%s"') % self.user.username
    description = property(get_description)

    def update_profile(self, new_preferred_language):
        self.defaultLanguage = new_preferred_language
        self.save()

    def get_contributions(self,  page=0,  page_size=20):
        return self.additions.order_by(
            '-createdAt')[page * page_size:(page + 1) * page_size - 1]

    def __unicode__(self):
        return (
            'RateableUser{defaultLanguage="%s",'
            'validatedAt="%s",lastLoggedOnAt="%s",user=[%s],super=[%s]}'
            % (
                self.defaultLanguage,
                self.validatedAt,
                self.lastLoggedOnAt,
                self.user,
                RateableStuff.__unicode__(self)))

    @classmethod
    def get(cls, **kwargs):
        return cls.__get(kwargs)

    @classmethod
    def __get(cls,  kwargs):
        if 'username' in kwargs and kwargs['username']:
            try:
                return User.objects.get(
                    username=kwargs['username']).get_profile()
            except User.DoesNotExist:
                raise RateableUser.Unknown('username',  kwargs['username'])
        elif 'email' in kwargs and kwargs['email']:
            try:
                return User.objects.get(email=kwargs['email']).get_profile()
            except User.DoesNotExist:
                raise RateableUser.Unknown('email',  kwargs['email'])
        else:
            raise ValueError()

    def begin_password_reset_process(self):
        request = PasswordResetRequest()
        request.expiresAt = datetime.datetime.now() + datetime.timedelta(
            days=settings.PASSWORD_RESET_EXPIRATION_DAYS)
        request.user = self
        request.save()
        request.begin_password_reset_process()
        return self

    @classmethod
    def register_new_user(cls, **kwargs):
        log.info("Beginning new user registration: '{0}'"
            .format(kwargs['username']))
        try:
            user = User.objects.get(username=kwargs['username'])
            if user.email != kwargs['email']:
                log.info("Username '{0}' already taken by '{1}'"
                    .format(kwargs['username'], user.email))
                raise RateableUser.ValidationException(
                    property='username',
                    messages=[_('Username taken.'
                        ' Please, choose another one.')])
            rateable_user = user.get_profile()
            if rateable_user.validatedAt != None:
                log.info("Account previously created but still not validated")
                raise RateableUser.ValidationException(
                    property='username',
                    messages=[_('Account already exists.'),
                        _('Have you forgotten your password?')])
            # account already created, but not yet validated.
            # Allow resending validation email
        except User.DoesNotExist:
            user = User.objects.create_user(
                kwargs['username'],
                kwargs['email'],
                kwargs['password1'])
            user.save()
            rateable_user = RateableUser(
                defaultLanguage=kwargs['preferred_language'],  user=user)
            rateable_user.save()
        validation = UserValidation()
        validation.expiresAt = datetime.datetime.now() + datetime.timedelta(
            days=settings.ACCOUNT_VALIDATION_EXPIRATION_DAYS)
        validation.user = rateable_user
        validation.save()
        validation.begin_account_validation_process()
        return user

    class ValidationException(UserWarning):

        def __init__(self, **kwargs):
            if 'property' in kwargs:
                self.property = kwargs['property']
            if 'messages' in kwargs:
                self.messages = kwargs['messages']

    class Unknown(UserWarning):

        def __init__(self, property_name,  property_value):
            self.property_name = property_name
            self.property_value = property_value


class UserBio(RateableStuff):
    theBio = models.TextField()
    user = models.OneToOneField('RateableUser', related_name='bio')

    def get_description(self):
        return _("Bio of user %(user)s") % {'user': user.user.username}
    description = property(get_description)


class UserValidation(models.Model):
    uuid = models.CharField(max_length=36, unique=True,  default=uuidMaker)
    requestedAt = models.DateTimeField(auto_now_add=True)
    expiresAt = models.DateTimeField()
    validatedAt = models.DateTimeField(null=True)
    user = models.ForeignKey('RateableUser')

    def begin_account_validation_process(self):
        log.info("Sending user validation email for '{0}' to '{1}'"
            .format(self.user.user.username, self.user.user.email))
        self.user.user.email_user(
            '[ratonator] (ACTION NEEDED) New account validation',
            render_to_string('registration_validation_email.html', {
                'key':
                    self.uuid,
                'days_to_expire':
                    settings.ACCOUNT_VALIDATION_EXPIRATION_DAYS})
        )
        log.info("Sent user validation email for '{0}' to '{1}'"
            .format(self.user.user.username, self.user.user.email))
        return self

    def end_account_validation_process(self):
        log.info("Received user validation request for '{0}'"
            .format(self.user.user.username))
        if self.validatedAt != None:
            log.info("User validation request ignored for '{0}'."
                " Already validated".format(self.user.user.username))
            raise UserValidation.ValidationException(
                message=_('Account already validated.'))
        if self.expiresAt < datetime.datetime.now():
            log.info("User validation request ignored for '{0}'."
                " Request expired".format(self.user.user.username))
            raise UserValidation.ValidationException(
                message=_('This validation link has been expired. '
                    'Please try registering again.'))
        self.validatedAt = datetime.datetime.now()
        self.save()
        self.user.validatedAt = datetime.datetime.now()
        self.user.save()
        log.info("User '{0}' validated.".format(self.user.user.username))
        return self

    @classmethod
    def get(cls, **kwargs):
        if 'key' in kwargs:
            try:
                return UserValidation.objects.get(uuid=kwargs['key'])
            except UserValidation.DoesNotExist:
                raise UserValidation.ValidationException(
                    message=_('Invalid link. Perhaps long expired.'
                        ' Please try registering again.'))
        raise ValueError('Required parameter not present')

    class ValidationException():

        def __init__(self, **kwargs):
            if 'message' in kwargs:
                self.message = kwargs['message']


class PasswordResetRequest(models.Model):
    uuid = models.CharField(max_length=36, unique=True, default=uuidMaker)
    requestedAt = models.DateTimeField(auto_now_add=True)
    expiresAt = models.DateTimeField()
    validatedAt = models.DateTimeField(null=True)
    user = models.ForeignKey('RateableUser')

    def begin_password_reset_process(self):
        log.info("Password reset requested by '{0}'"
            .format(self.user.user.username))
        email = EmailMessage()
        email.subject = '[ratonator] (ACTION NEEDED) Password reset requested'
        email.body = render_to_string(
            'password_reset_email.html', {
                'key': self.uuid,
                'days_to_expire':
                    settings.PASSWORD_RESET_EXPIRATION_DAYS})
        email.from_email = 'mailer@ratonator.com'
        email.to = [self.user.user.email]
        email.send()
        return self

    def end_password_reset_process(self,  password1,  password2):
        log.info("Password reset requested confirmed from email by '{0}'"
            .format(self.user.user.username))
        if self.expiresAt < datetime.datetime.now():
            log.info(
                "Password reset requested confirmed from email by '{0}'"
                " has been expired. Ignored."
                .format(self.user.user.username))
            raise PasswordResetRequest.ValidationException(
                property='password1',
                messages=[
                    _('This password reset request expired. '),
                    _(
                        'Request another one if you still want'
                        ' to reset your password.')])
        if not self.validatedAt == None:
            log.info("Password reset requested confirmed from email by '{0}'"
                " has been already consumed. Ignored."
                .format(self.user.user.username))
            raise PasswordResetRequest.ValidationException(
                property='password1',
                messages=[
                    _('This password reset request was already consumed. '),
                    _('Request another one if you still want to reset'
                        ' your password.')]
            )
        if password1 != password2:
            log.info("Password reset requested confirmed from email by '{0}'"
                " but passwords doesn't match. Ignored."
                .format(self.user.user.username))
            raise PasswordResetRequest.ValidationException(
                property='password2',
                messages=[_('Passwords do not match')])
        self.validatedAt = datetime.datetime.now()
        self.save()
        self.user.user.set_password(password1)
        self.user.user.save()
        log.info("New password set for user '{0}'"
            .format(self.user.user.username))
        return self

    @classmethod
    def get(cls, **kwargs):
        if 'key' in kwargs:
            return PasswordResetRequest.objects.get(uuid=kwargs['key'])
        raise ValueError('Required parameter not present')

    class ValidationException(UserWarning):

        def __init__(self, **kwargs):
            if 'messages' in kwargs:
                self.messages = kwargs['messages']
            if 'property' in kwargs:
                self.property = kwargs['property']
