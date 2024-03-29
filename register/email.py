from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_welcome_email(name,receiver):
    subject='Welcome to AwwardMe'
    sender='jeffersondev29@gmail.com'
    
    #passing in the context variable
    text_content=render_to_string('email/email.txt',{'name': name})
    html_content=render_to_string('email/email.html',{'name':name})
    
    msg=EmailMultiAlternatives(subject,text_content,sender,[receiver])
    msg.attach_alternative(html_content,'text/html')
    msg.send()