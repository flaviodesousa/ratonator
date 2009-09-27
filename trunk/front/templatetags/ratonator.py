from django import template
from front.models import *
import re



register = template.Library()


follow_re = re.compile('follow=(True|False)')
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



rateable_template = template.loader.get_template('rateable_template.html')
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
        
        return rateable_template.render(c)
