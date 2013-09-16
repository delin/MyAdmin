import os
import subprocess
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
import pwd
import grp
from MyAdmin.functions import prepare_data, modules_update, get_system_users, get_system_groups, replace_in_file
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
@require_http_methods(["GET"])
def page_log_view(request, log_id=0):
    page_title = _("Log view")

    try:
        view_log = Log.objects.get(id=log_id)
    except Log.DoesNotExist as e:
        messages.error(request,  e)
        return redirect('logs')

    return render(request, "pages/page_log_view.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'view_log': view_log,
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


@login_required
@require_http_methods(["GET"])
def page_users(request):
    page_title = _("All Users")

    return render(request, "pages/page_users.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'users': get_system_users(),
    })


@login_required
@require_http_methods(["GET", "POST"])
def page_user_add(request):
    page_title = _("Create new user")

    c = {}
    c.update(csrf(request))

    if request.method == "POST":
        if 'login' and 'password' in request.POST:
            login = request.POST['login']
            password = request.POST['password']

            useradd_options = ""
            if 'view_advanced' in request.POST:
                if 'create_home' and 'home_dir' in request.POST and len(request.POST) > 0:
                    useradd_options += " -m -d %s" % request.POST['home_dir']

                if 'select-groups' in request.POST:
                    groups_list = request.POST.getlist('select-groups')
                    if len(groups_list) > 0:
                        groups = ",".join(str(item) for item in groups_list)

                        useradd_options += " -G %s" % groups

                if 'create_user_group' in request.POST:
                    useradd_options += " -U"
                else:
                    useradd_options += " -N"

                if 'set_other_shell' and 'other_shell' in request.POST:
                    if os.access(request.POST['other_shell'], os.X_OK):
                        useradd_options += " -s %s" % request.POST['other_shell']
                else:
                    if 'select-shell' in request.POST:
                        if os.access(request.POST['select-shell'], os.X_OK):
                            useradd_options += " -s %s" % request.POST['select-shell']

                if 'comment' in request.POST and len(request.POST['comment']) > 0:
                    useradd_options += " -c \"%s\"" % request.POST['comment']

                if 'create_system_account' in request.POST:
                    useradd_options += " -r"

            useradd = "/usr/bin/useradd %s %s" % (useradd_options, login)
            passwd_string = "echo -e \"%s\\n%s\" | passwd %s" % (password, password, login)

            try:
                useradd_os = os.WEXITSTATUS(os.system(useradd))
                Log(
                    action=4,
                    user=request.user,
                    os_system=useradd,
                    os_system_code=useradd_os,
                ).save()
            except BaseException as e:
                Log(
                    action=4,
                    user=request.user,
                    os_system=useradd,
                    os_system_code=-1,
                ).save()
                messages.error(request, e)
                return redirect('user_add')

            if useradd_os == 0:
                passwd_os = os.WEXITSTATUS(os.system(passwd_string))
                Log(
                    action=5,
                    user=request.user,
                    os_system=passwd_string,
                    os_system_code=passwd_os,
                ).save()

                if passwd_os == 0:
                    messages.success(request, _("User") + " " + login + " " + _("created"))
                else:
                    messages.error(request,  passwd_os)

                if 'create_and_next' in request.POST:
                    return redirect('user_add')

                return redirect('users')
            elif useradd_os == 1:
                messages.error(request,  _("Can't update password file"))
            elif useradd_os == 2:
                messages.error(request,  _("Invalid command syntax"))
            elif useradd_os == 3:
                messages.error(request,  _("Invalid argument to option"))
            elif useradd_os == 4:
                messages.error(request,  _("UID already in use (and no -o)"))
            elif useradd_os == 6:
                messages.error(request,  _("Specified group doesn't exist"))
            elif useradd_os == 9:
                messages.error(request,  _("Username already in use"))
            elif useradd_os == 10:
                messages.error(request,  _("Can't update group file"))
            elif useradd_os == 12:
                messages.error(request,  _("Can't create home directory"))
            elif useradd_os == 13:
                messages.error(request,  _("Can't create mail spool"))
            else:
                messages.error(request,  useradd_os)

        return redirect('user_add')
    else:
        shells = []
        default_shells = ['/bin/bash', '/bin/sh', '/bin/zsh', '/bin/dash', '/bin/false', '/dev/null']
        for shell in default_shells:
            if os.access(shell, os.X_OK):
                shells.append(shell)

        return render(request, "pages/page_user_add.html", {
            'page_title': page_title,
            'data': prepare_data(request),
            'users': get_system_users(),
            'groups': get_system_groups(),
            'shells': shells,
        })


@login_required
@require_http_methods(["GET"])
def page_user_view(request, user_uid=0):
    page_title = _("User view")

    user_view = pwd.getpwuid(int(user_uid))
    if not user_view:
        messages.error(request, _("User not exist"))
        return redirect('users')

    user_group = grp.getgrgid(user_view[3])
    user_groups = user_group

    return render(request, "pages/page_user_view.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'user_view': user_view,
        'user_group': user_group[0],
        'user_groups': user_groups,
    })


@login_required
@require_http_methods(["GET"])
def page_user_group_add(request):
    page_title = _("Create new group")

    return render(request, "pages/page_user_group_add.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'users': get_system_users(),
    })