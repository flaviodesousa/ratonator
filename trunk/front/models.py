#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Avg, Count
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
import datetime
import uuid

RATE_CHOICES = (
    (10, _('Impossibly good')),
    ( 9, _('Best ever')),
    ( 8, _('Excellent')),
    ( 7, _('Very good')),
    ( 6, _('Good')),
    ( 5, _('Regular')),
    ( 4, _('Weak')),
    ( 3, _('Bad')),
    ( 2, _('Very Bad')),
    ( 1, _('Worse ever')),
    ( 0, _('Impossibly bad'))
)



def uuidMaker():
    return str(uuid.uuid4())



class Language(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=64, unique=True)
    nativeName = models.CharField(max_length=64, unique=True)

    @classmethod
    def choices(cls):
        return [(l.code, l.nativeName) for l in Language.objects.all().order_by('nativeName')]



def post_save_handler(sender, **kwargs):
    if sender is User and kwargs['created']:
        rateable_user = RateableUser(defaultLanguage='en', user=kwargs['instance'])
        rateable_user.save()



post_save.connect(post_save_handler)



class RateableStuff(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    # FIXME: Set on new votes, new definitions and new classifications
    # TODO: Split time stamp for voting, defining and classifying
    lastTouchedAt = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey('RateableUser', related_name='additions', null=True)
    uuid = models.CharField(max_length=36, unique=True, default=uuidMaker)
    # TODO: Add fields with precalculations of rates and votes (partialAt, partialVotes, partialAverage)

    def addRate(self, rate_value, comments_text, user):
        try:
            existing = self.rates.filter(createdBy=user).get(superseder__isnull=True)
        except Rate.DoesNotExist:
            existing = None
        rate = Rate(theRate=rate_value, comments=comments_text, subject=self, createdBy=user)
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
        return 'RateableStuff{createdAt="%s",lastTouchedAt="%s",uuid="%s",createdBy=[%s]}' % (self.createdAt,self.lastTouchedAt,self.uuid, self.createdBy)

    def getSample(self, max_definitions=5, max_rates=5):
        rates = self.rates.filter(superseder__isnull=True).order_by('-createdAt')[:max_rates]
        return rates

    def __aggregates(self):
        try:
            return self.__aggregate_cache
        except AttributeError:
            self.__aggregate_cache = self.rates.filter(superseder__isnull=True).aggregate(Avg('theRate'),Count('theRate'))
            return self._aggregate_cache

    def get_average_rate(self):
        return round(self.__aggregates()['theRate__avg'], 1)

    def get_rate_count(self):
        return self.__aggregates()['theRate__count']

    average_rate = property(get_average_rate)
    rate_count = property(get_rate_count)



class Rate(RateableStuff):
    theRate = models.SmallIntegerField()
    comments = models.TextField(null=True)
    superseder = models.OneToOneField('Rate', related_name='superseded', null=True)
    subject = models.ForeignKey('RateableStuff', related_name='rates')

    def __unicode__(self):
        return 'Rate{theRate="%d",comments="%s",superseder=[%s],subject=[%s],super=[%s]}' % (self.theRate,self.comments,self.superseder,self.subject,RateableStuff.__unicode__(self))



class NameableRateableStuff(RateableStuff):
    name = models.CharField(max_length=255)
    # FIXME: Not being automatically slugged
    # TODO: Automatic slug set on save
    nameSlugged = models.SlugField(max_length=255)
    language = models.CharField(max_length=2)
    disambiguator = models.ForeignKey('Disambiguator', related_name='ambiguousSubjects', null=True)

    def __unicode__(self):
        return 'NameableRateableStuff{name="%s",nameSlugged="%s",language="%s",super=[%s]}' % (self.name, self.nameSlugged, self.language, RateableStuff.__unicode__(self))

    class Meta:
        unique_together = (("language", "name"), ("language", "nameSlugged"),)



class Aspect(NameableRateableStuff):
    subjects = models.ManyToManyField('ClassifiableRateableStuff', related_name='aspects')



class AspectRate(Rate):
    aspect = models.ForeignKey('Aspect')
    baseRate = models.ForeignKey('Rate', related_name='ratingAspects')



class ClassifiableRateableStuff(NameableRateableStuff):

    @classmethod    
    def get(cls, language_filter, name_slugged):
        return ClassifiableRateableStuff.objects.filter(language=language_filter).get(nameSlugged=name_slugged)

    @classmethod
    def hotSubjects(cls, language_filter, days=1,  page=1,  max_subjects=20):
        one_day_ago = datetime.datetime.now() + datetime.timedelta(days=-days)
        slice = (page - 1) * max_subjects
        return ClassifiableRateableStuff.objects.filter(language=language_filter).filter(lastTouchedAt__gte = one_day_ago).filter(rates__superseder__isnull=True).annotate(hotness=Sum('rates__theRate')).filter(hotness__isnull=False).order_by('-hotness')

    @classmethod
    def newSubjects(cls, language_filter, page=1,  max_subjects=100):
        slice = (page - 1) * max_subjects
        return ClassifiableRateableStuff.objects.filter(language=language_filter).order_by('-createdAt')[slice:max_subjects]

    @classmethod
    def topSubjects(cls,  language_filter, page=1, max_subjects=100):
        slice = (page - 1) * max_subjects
        #return ClassifiableRateableStuff.objects.filter(language=language_filter).filter(rates__superseder__isnull=False).annotate(topness=Avg('rates__theRate')).order_by('-topness')[slice:max_subjects]
        return ClassifiableRateableStuff.objects.filter(language=language_filter).filter(rates__superseder__isnull=True).annotate(topness=Avg('rates__theRate')).filter(topness__isnull=False).order_by('-topness')[slice:max_subjects]

    @classmethod
    def addSubject(cls, name, language, user, definition=None):
        new_subject = ClassifiableRateableStuff()
        new_subject.nameSlugged = new_subject.name = name
        new_subject.language = language
        new_subject.createdBy = user
        new_subject.save()

        if not definition == None:
            new_subject.addDefinition(definition, user)

        return new_subject

    def sample(self, max_definitions=5, max_rates=5):
        rates = NameableRateableStuff.getSample(self, max_rates)
        definitions = self.definitions.order_by('-createdAt')[:max_definitions]
        subjects_above = [ above for above in self.categories.all() ]
        subjects_below = [ below for below in self.subjects.all() ]
        return (definitions, rates, subjects_above, subjects_below)

    def addDefinition(self, definition_text, user):
        definition = Definition(theDefinition=definition_text, subject=self, createdBy=user)
        definition.save()
        self.touch()
        return self

    def addCategory(self, category_name, user):
        try:
            adding_category = ClassifiableRateableStuff.get(self.language, category_name)
        except ClassifiableRateableStuff.DoesNotExist:
            adding_category = ClassifiableRateableStuff.addSubject(category_name, self.language, user)
        classification = Classification(subject=self, category=adding_category, createdBy=user)
        classification.save()
        self.touch()
        return self

    def __unicode__(self):
        return "ClassifiableRateableStuff{super=[%s]}" % NameableRateableStuff.__unicode__(self)



class Classification(RateableStuff):
    subject = models.ForeignKey('ClassifiableRateableStuff', related_name='categories')
    category = models.ForeignKey('ClassifiableRateableStuff', related_name='subjects')

    class Meta:
        unique_together = (('subject','category'),)



class Definition(RateableStuff):
    theDefinition = models.TextField()
    #superseder = models.OneToOneField('Definition', related_name='superseded', null=True)
    subject = models.ForeignKey('ClassifiableRateableStuff', related_name='definitions')



class Disambiguator(models.Model):
    commonTerm = models.CharField(max_length=255)
    language = models.CharField(max_length=2)

    def __unicode__(self):
        return 'Disambiguator{commonTerm="%s",language="%s"}' % (commonTerm, language)

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

    def __unicode__(self):
        return 'RateableUser{defaultLanguage="%s",validatedAt="%s",lastLoggedOnAt="%s",user=[%s],super=[%s]}' % (self.defaultLanguage,self.validatedAt,self.lastLoggedOnAt,self.user,RateableStuff.__unicode__(self))

    def get(**kwargs):
        if kwargs['email']:
            return RateableUser.objects.get(email=email)



class UserValidation(models.Model):
    uuid = models.CharField(max_length=36, unique=True)
    requestedAt = models.DateTimeField(auto_now_add=True)
    expiresAt = models.DateTimeField()
    validatedAt = models.DateTimeField(null=True)
    user = models.ForeignKey('RateableUser')
