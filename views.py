def singup(request):
    if request.method == 'POST':
        form = SingUpForm(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
               'secret':settings.GOOGLE_RECAPTCHA_SECRET_KEY,
               'response':recaptcha_response
            }
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
            response = urllib2.urlopen(req)
            result = json.load(response)
            if result['success']:
                user = form.save(commit=False)
                user.is_active = False
                user.is_admin = False
                user.save()
                username = user.username
                current_site = get_current_site(request)
                subject = "Activate your Search site Account"
                message = render_to_string('account_activation_email.html',{
                 'user': user,
                 'domain': current_site.domain,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': account_activation_token.make_token(user),
                 })
                user.email_user(subject,message,username)
                return redirect('account_activation_sent')
            else:
                messages.error(request,"Invalid reCaptcha.Please try again.")
                return redirect('singup')

    else:
        form = SingUpForm()
    return render(request,'singup.html',{'form':form})


def activate(request, uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,MyUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_comfirmed = True
        user.save()
        return HttpResponseRedirect('/login')
    else:
        return render(request,'account_activation_invalid.html')

def account_activation_sent(request):
    return render(request,'account_activation_sent.html')
