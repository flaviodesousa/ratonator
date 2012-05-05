#! /usr/bin/python

import sys
import os

def setup_environment():
    pathname = os.path.dirname(sys.argv[0])
    sys.path.append(os.path.abspath(pathname))
    sys.path.append(os.path.normpath(os.path.join(os.path.abspath(pathname), '../')))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Must set up environment before imports.
setup_environment()

from django.core.mail import EmailMessage
from django.contrib.auth.models import User

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    if len(argv) < 4:
        print r'Usage: %s <recipient email> "subject" "message" [files to send...]'
        exit(1)

    recipient = argv[1]
    subject = argv[2]
    message = argv[3]
    files = argv[4:]

    email = EmailMessage()
    email.subject = subject
    email.body = message
    email.from_email = 'mailer@ratonator.com'
    email.to = [ recipient ]
    
    for file in files:
        email.attach_file(file)
    
    email.send()

if __name__ == '__main__':
    main()
