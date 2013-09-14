from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
from MyAdmin.functions import prepare_data, modules_update
from main.models import Log


@csrf_protect
@require_http_methods(["GET", "POST"])
def page_login(request):
    if request.user.is_authenticated():
        return redirect('home', permanent=False)

    page_title = _("Sign In")
    content = {
        'next': "/",
    }

    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST['username'].strip()
            password = request.POST['password']

            if 'next' in request.GET:
                next_page = request.GET['next']
                if not next_page or next_page in ['/logout', '/logout/', 'logout', 'logout/']:
                    next_page = "/"
            else:
                next_page = "/"

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)

                    return redirect(next_page, permanent=False)
                else:
                    messages.error(request, _("This account disabled."))
            else:
                messages.error(request, _("Wrong username or password."))

        return redirect('login', permanent=False)

    return render(request, 'pages/page_login.html', {
        'page_title': page_title,
        'data': prepare_data(request),
        'content': content
    })


@login_required()
def page_logout(request):
    logout(request)
    return redirect('login', permanent=False)


@login_required
@require_http_methods(["GET"])
def page_home(request):
    page_title = _("Home")

    content = {}

    return render(request, "pages/page_home.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'content': content,
    })


@login_required
@require_http_methods(["GET"])
def page_about(request):
    page_title = _("About")

    return render(request, "pages/page_about.html", {
        'page_title': page_title,
        'data': prepare_data(request),
    })


@login_required
@require_http_methods(["GET"])
def page_logs(request):
    page_title = _("Logs")

    logs = Log.objects.all()

    return render(request, "pages/page_logs.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'logs': logs,
    })


@login_required
@require_http_methods(["GET", "POST"])
def page_modules(request):
    page_title = _("Modules")

    if request.method == "POST":
        if 'update' in request.POST:
            new_modules = modules_update(request)

            if new_modules > 0:
                messages.success(request, str(new_modules) + " " + _("Module is installed"))
            else:
                messages.info(request, _("No new modules"))

        return redirect('modules')

    return render(request, "pages/page_modules.html", {
        'page_title': page_title,
        'data': prepare_data(request),
    })