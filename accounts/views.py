from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import redirect, render

from .forms import EmailAuthenticationForm, ProfileForm, SignUpForm

def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('products:home')
    return render(request, 'accounts/signup.html', {'form': form})


class LoginView(DjangoLoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})
