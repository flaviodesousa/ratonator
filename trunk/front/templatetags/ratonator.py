from django import template
from front.models import *
import re



UNLOADED = 'unloaded'
register = template.Library()

# preloads

_FOLLOW_RE = re.compile('follow=(True|False)')

_RATEABLE_TEMPLATE = UNLOADED
def get_RATEABLE_TEMPLATE():
    global _RATEABLE_TEMPLATE
    if _RATEABLE_TEMPLATE == UNLOADED:
        _RATEABLE_TEMPLATE = template.loader.get_template('rateable_tag.html')
    return _RATEABLE_TEMPLATE

_RATES_TEMPLATE = UNLOADED
def get_RATES_TEMPLATE():
    global _RATES_TEMPLATE
    if _RATES_TEMPLATE == UNLOADED:
        _RATES_TEMPLATE = template.loader.get_template('rates_tag.html')
    return _RATES_TEMPLATE



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
        follow_match = _FOLLOW_RE.match(tokens[2])
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
        
        return get_RATEABLE_TEMPLATE().render(c)




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

        return get_RATES_TEMPLATE().render(c)
