import os
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
from MyAdmin.functions import prepare_data, modules_update, system_cmd
from system_tools.services import SystemServices
from main.models import Log
from system_tools.users import SystemUsers


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

    return render(request, "pages/page_home.html", {
        'page_title': page_title,
        'data': prepare_data(request),
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
    user_management = SystemUsers()

    return render(request, "pages/page_users.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'users': user_management.get_users(),
    })


@login_required
@require_http_methods(["GET", "POST"])
def page_user_add(request):
    page_title = _("Create new user")

    c = {}
    c.update(csrf(request))

    user_management = SystemUsers()

    if request.method == "POST":
        if 'login' and 'password' in request.POST:
            login = request.POST['login']
            password = request.POST['password']

            if 'set_other_shell' and 'other_shell' in request.POST:
                shell = request.POST['other_shell']
            else:
                if 'select-shell' in request.POST:
                    shell = request.POST['select-shell']
                else:
                    shell = "/bin/false"

            exitcode = user_management.create_user(
                login=login,
                password=password,
                home_dir=request.POST.get("home_dir"),
                in_groups=request.POST.getlist('select-groups'),
                create_group=request.POST.get("create_user_group"),
                shell=shell,
                comment=request.POST.get("comment"),
                is_system_user=request.POST.get("create_system_account"),
            )

            Log(
                action=4,
                user=request.user,
                os_system_code=exitcode,
            ).save()

            if exitcode == 0:
                messages.success(request, _("User") + " " + login + " " + _("created"))

                if 'create_and_next' in request.POST:
                    return redirect('user_add')

                return redirect('users')
            elif exitcode == 1:
                messages.error(request,  _("Can't update password file"))
            elif exitcode == 2:
                messages.error(request,  _("Invalid command syntax"))
            elif exitcode == 3:
                messages.error(request,  _("Invalid argument to option"))
            elif exitcode == 4:
                messages.error(request,  _("UID already in use (and no -o)"))
            elif exitcode == 6:
                messages.error(request,  _("Specified group doesn't exist"))
            elif exitcode == 9:
                messages.error(request,  _("Username already in use"))
            elif exitcode == 10:
                messages.error(request,  _("Can't update group file"))
            elif exitcode == 12:
                messages.error(request,  _("Can't create home directory"))
            elif exitcode == 13:
                messages.error(request,  _("Can't create mail spool"))
            else:
                messages.error(request,  _("Unknown exit code: ") + exitcode)

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
            'users': user_management.get_users(),
            'groups': user_management.get_groups(),
            'shells': shells,
        })


@login_required
@require_http_methods(["GET", "POST"])
def page_user_view(request, user_uid=0):
    page_title = _("User view")

    c = {}
    c.update(csrf(request))

    user_management = SystemUsers()
    user_info = user_management.get_user(uid=user_uid)
    if not user_info:
        messages.error(request, _("User not exist"))
        return redirect('users')

    return render(request, "pages/page_user_view.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'user_uid': user_uid,
        'user_info': user_info,
    })


@login_required
@require_http_methods(["POST"])
def page_user_edit(request, user_uid=0):
    c = {}
    c.update(csrf(request))

    user_management = SystemUsers()
    user_info = user_management.get_user(uid=user_uid)
    if not user_info:
        messages.error(request, _("User not exist"))
        return redirect('users')

    if "btn-changepass" and "new_password" and "repeat_password" in request.POST:
        if request.POST.get("new_password") == request.POST.get("repeat_password"):
            password = request.POST.get("new_password")

            exitcode = user_management.change_password(user_info['name'], password)
            if exitcode == 0:
                messages.success(request, _("Password changed"))
            else:
                messages.error(request, _("Password not changed, see logs for more info"))
        else:
            messages.error(request, _("Passwords not match"))

        return redirect('user_view', user_uid=user_uid)
    elif "btn-userdel" and "i_know_what_i_am_doing" in request.POST:
        if user_info['name'] == 'root':
            messages.error(request, _("You're crazy, I will not do it!"))
            return redirect('users')

        exitcode = user_management.delete_user(user_info['name'],
                                               force=request.POST.get("userdel_force"),
                                               remove_home=request.POST.get("userdel_force"))
        if exitcode == 0:
            messages.success(request, _("User removed"))
        elif exitcode == 1:
            messages.error(request, _("Can't update password file"))
        elif exitcode == 2:
            messages.error(request, _("Invalid command syntax"))
        elif exitcode == 6:
            messages.error(request, _("Specified user doesn't exist"))
        elif exitcode == 8:
            messages.error(request, _("User currently logged in"))
        elif exitcode == 10:
            messages.error(request, _("Can't update group file"))
        elif exitcode == 12:
            messages.error(request, _("Can't remove home directory"))
        else:
            messages.error(request, _("User not removed, see logs for more info"))

    return redirect('users')


@login_required
@require_http_methods(["GET"])
def page_user_group_add(request):
    page_title = _("Create new group")

    user_management = SystemUsers()
    return render(request, "pages/page_user_group_add.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'users': user_management.get_users(),
    })


@login_required
@require_http_methods(["GET", "POST"])
def page_services(request):
    page_title = _("Services")

    system_services = SystemServices()
    services = system_services.list()

    return render(request, "pages/page_services.html", {
        'page_title': page_title,
        'data': prepare_data(request),
        'services': services,
    })


@login_required
@require_http_methods(["POST"])
def page_service_action(request, service_name):
    if "prev_page" in request.POST:
        prev_page = request.POST.get("prev_page")
    else:
        prev_page = "services"

    system_service = SystemServices()

    if 'btn-reload' in request.POST:
        if system_service.reload(service_name):
            messages.success(request, _("Service reloaded: ") + service_name)
        else:
            messages.error(request, _("Service not reloaded: ") + service_name)
    elif 'btn-restart' in request.POST:
        if system_service.restart(service_name):
            messages.success(request, _("Service restarted: ") + service_name)
        else:
            messages.error(request, _("Service not restarted: ") + service_name)
    elif 'btn-stop' in request.POST:
        if system_service.stop(service_name):
            messages.success(request, _("Service stopped: ") + service_name)
        else:
            messages.error(request, _("Service not stopped: ") + service_name)
    elif 'btn-start' in request.POST:
        if system_service.start(service_name):
            messages.success(request, _("Service started: ") + service_name)
        else:
            messages.error(request, _("Service not started: ") + service_name)

    return redirect(prev_page)