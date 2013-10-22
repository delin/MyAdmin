from crypt import crypt
from operator import itemgetter
import subprocess
import grp
import pwd
import uuid
from django.utils.translation import ugettext as _

__author__ = 'delin'


class SystemUsers():
    def __init__(self):
        pass

    def _hash_password(self, password):
        return crypt(password, uuid.uuid4().hex[:2])

    def _exit_messages(self, exit_code):
        if exit_code == 0:
            return_message = _("Success")
        elif exit_code == 1:
            return_message = _("Can't update password file")
        elif exit_code == 2:
            return_message = _("Invalid command syntax")
        elif exit_code == 3:
            return_message = _("Invalid argument to option")
        elif exit_code == 4:
            return_message = _("UID already in use (and no -o)")
        elif exit_code == 6:
            return_message = _("Specified group or user doesn't exist")
        elif exit_code == 8:
            return_message = _("User currently logged in")
        elif exit_code == 9:
            return_message = _("Username already in use")
        elif exit_code == 10:
            return_message = _("Can't update group file")
        elif exit_code == 10:
            return_message = _(
                "Insufficient space to move the home directory (-m option). Other update requests will be implemented/")
        elif exit_code == 12:
            return_message = _("Can't create home directory")
        elif exit_code == 13:
            return_message = _("Can't create mail spool")
        elif exit_code == 14:
            return_message = _("Can't update SELinux user mapping")
        else:
            return_message = _("Unknown exit code: ") + exit_code

        return return_message

    def get_users(self):
        system_groups = grp.getgrall()
        system_users = pwd.getpwall()

        users = []
        for user in system_users:
            pw_name = user[0]
            pw_uid = user[2]
            pw_gid = user[3]
            pw_gecos = user[4]
            pw_dir = user[5]
            pw_shell = user[6]

            user_groups = []
            for group in system_groups:
                gr_name = group[0]
                gr_gid = group[2]
                gr_mem = group[3]

                if pw_name in gr_mem:
                    user_groups.append({
                        'name': gr_name,
                        'gid': gr_gid,
                    })

            users.append({
                'name': pw_name,
                'uid': int(pw_uid),
                'gid': int(pw_gid),
                'comment': pw_gecos,
                'groups': user_groups,
                'home_dir': pw_dir,
                'shell': pw_shell,
            })

        return sorted(users, key=itemgetter('uid'))

    def get_groups(self):
        system_groups = grp.getgrall()

        user_groups = []
        for group in system_groups:
            user_groups.append({
                'name': group[0],
                'gid': group[2],
                'members': group[3],
            })

        return user_groups

    def get_user(self, login=None, uid=None):
        if login:
            user = pwd.getpwnam(login)
        elif uid:
            user = pwd.getpwuid(int(uid))
        else:
            return False

        if not user:
            return False

        all_groups = self.get_groups()
        user_groups = []
        for group in all_groups:
            if user[0] in group['members']:
                user_groups.append(group)

        return {
            'name': user[0],
            'uid': int(user[2]),
            'gid': int(user[3]),
            'group': grp.getgrgid(int(user[3]))[0],
            'comment': user[4],
            'groups': user_groups,
            'home_dir': user[5],
            'shell': user[6],
        }

    def create_group(self, group, force=False, gid=None, non_unique=False, password=None, is_system_group=False,
                     chroot=None):
        options = []

        # Force?
        if force:
            options.append("--force")

        # GID
        if gid and int(gid) > 0:
            options.append("--gid")
            options.append(gid)

        # Allow create non unique GID
        if non_unique:
            options.append("--non-unique")

        # Password
        if password:
            options.append("--password")
            options.append(self._hash_password(password))

        # Is system user?
        if is_system_group:
            options.append('--system')

        # In chroot dir?
        if chroot:
            options.append("--root")
            options.append(chroot)

        options.append(group)

        exit_code = subprocess.call(["groupadd"] + options)

        return exit_code, self._exit_messages(exit_code)

    def create_user(self, login, password=None, home_dir=None, in_groups=None, create_group=True, shell="/bin/false",
                    comment=None, is_system_user=False, chroot=None):
        if not home_dir:
            home_dir = "/home/" + login

        # Home dir, comment, shell
        options = ['--create-home', '--home-dir', home_dir, '--shell', shell]

        # Comment
        if comment and len(comment) > 0:
            options.append("--comment")
            options.append(comment)

        # Password
        if password:
            options.append("--password")
            options.append(self._hash_password(password))

        # Groups
        if in_groups:
            options.append('--groups')
            options.append(",".join(str(item) for item in in_groups))

        # Create self-group
        if create_group:
            options.append('--user-group')

        # Is system user?
        if is_system_user:
            options.append('--system')

        # In chroot dir?
        if chroot:
            options.append("--root")
            options.append(chroot)

        options.append(login)

        exit_code = subprocess.call(["useradd"] + options)

        return exit_code, self._exit_messages(exit_code)

    def change_password(self, login, new_password, chroot=None):
        options = ["--password", self._hash_password(new_password)]

        # In chroot dir?
        if chroot:
            options.append("--root")
            options.append(chroot)

        options.append(login)

        exit_code = subprocess.call(["usermod"] + options)

        return exit_code, self._exit_messages(exit_code)

    def delete_user(self, login, force=False, remove_home=False, chroot=None):
        options = []

        # Force?
        if force:
            options.append("--force")

        # Remove Home dir?
        if remove_home:
            options.append("--remove")

        # In chroot dir?
        if chroot:
            options.append("--root")
            options.append(chroot)

        options.append(login)

        exit_code = subprocess.call(["userdel"] + options)

        return exit_code, self._exit_messages(exit_code)