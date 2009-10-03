from django import template
from front.models import *
import re



UNLOADED = 'unloaded'
register = template.Library()
# preloads
follow_re = re.compile('follow=(True|False)')

_rateable_template = UNLOADED
def get_rateable_template():
    global _rateable_template
    if _rateable_template == UNLOADED:
        _rateable_template = template.loader.get_template('rateable_tag.html')
    return _rateable_template

_rates_template = UNLOADED
def get_rates_template():
    global _rates_template
    if _rates_template == UNLOADED:
        _rates_template = template.loader.get_template('rates_tag.html')
    return _rates_template



@register.tag
def rateable(parser, token):
    try:
        tokens = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    if len(tokens) < 2:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    
    subject_varname = tokens[1]
    follow = False
    
    if len(tokens) > 2:
        follow_match = follow_re.match(tokens[2])
        if not follow_match:
            raise template.TemplateSyntaxError, "%r tag 2nd argument is follow=(True|False)" % token.contents.split()[0]
        follow = follow_match.group(1) == 'True'

    return RateableNode(subject_varname, follow)



@register.tag
def rates(parser, token):
    try:
        tokens = token.split_contents()
        if len(tokens) != 2:
            raise ValueError
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires a single argument" % token.contents.split()[0]

    subject_varname = tokens[1]

    return RatesNode(subject_varname)



class RateableNode(template.Node):

    def __init__(self, subject_varname, follow):
        self.subject_ref = template.Variable(subject_varname)
        self.user_ref = template.Variable('user')
        self.follow = follow

    def render(self, context):
        c = template.Context({
            'subject': self.subject_ref.resolve(context),
            'user': self.user_ref.resolve(context), 
            'follow': self.follow
        })
        
        return get_rateable_template().render(c)




class RatesNode(template.Node):

    def __init__(self, subject_varname):
        self.subject_ref = template.Variable(subject_varname)
        self.user_ref = template.Variable('user')
    
    def render(self, context):
        subject = self.subject_ref.resolve(context)
        rates = subject.rates.all()
        c = template.Context({
            'subject':subject, 
            'rates': rates, 
            'user':self.user_ref.resolve(context)
        })

        return get_rates_template().render(c)
