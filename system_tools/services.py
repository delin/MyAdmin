import os
import re
import subprocess

__author__ = 'delin'


class SystemServices():
    """
    init_type:
     0 = Unknown
     1 = System-V (Debian, Ubuntu)
     2 = SystemD (Archlinux)
    """
    init_type = 0

    def __init__(self):
        if os.access("/usr/sbin/service", os.X_OK):
            self.init_type = 1
        elif os.access("/usr/sbin/systemctl", os.X_OK):
            self.init_type = 2

    # Systemd   (Arch linux)
    def _init_systemd_list(self):
        services = subprocess.check_output(["systemctl", "list-units", "--no-pager", "--no-legend"]).splitlines(False)
        services_list = []

        for service in services:
            array = service.split()
            name = re.search('^[a-zA-Z@0-9\-:]+', array[0]).group(0)
            autostart = array[1]
            st = array[2]

            status = None
            if st == 'running':
                status = True
            elif st == 'failed':
                status = False

            services_list.append({
                'name': name,
                'autostart': autostart,
                'status': status,
            })

        return services_list

    def _init_systemd_status(self, service):
        return not subprocess.call(["systemctl", "status", service])

    def _init_systemd_start(self, service):
        if not self._init_systemd_status(service):
            return not subprocess.call(["systemctl", "start", service])
        else:
            return False

    def _init_systemd_stop(self, service):
        if self._init_systemd_status(service):
            return not subprocess.call(["systemctl", "stop", service])
        else:
            return False

    def _init_systemd_restart(self, service):
        return not subprocess.call(["systemctl", "restart", service])

    def _init_systemd_reload(self, service):
        return not subprocess.call(["systemctl", "reload", service])

    # System-V  (Debian)
    def _init_systemv_list(self):
        services = subprocess.check_output(["service", "--status-all"]).splitlines(False)
        services_list = []

        for service in services:
            st = re.search('(?<= )[\?\+\-]', service).group(0)
            status = None
            if st == '+':
                status = True
            elif st == '-':
                status = False

            services_list.append({
                'name': re.search('[a-zA-Z@0-9-]{2,}', service).group(0),
                'status': status,
            })

        return services_list

    def _init_systemv_status(self, service):
        return not subprocess.call(["service", service, "status"])

    def _init_systemv_start(self, service):
        if not self._init_systemv_status(service):
            return not subprocess.call(["service", service, "start"])
        else:
            return False

    def _init_systemv_stop(self, service):
        if self._init_systemv_status(service):
            return not subprocess.call(["service", service, "stop"])
        else:
            return False

    def _init_systemv_restart(self, service):
        return not subprocess.call(["service", service, "restart"])

    def _init_systemv_reload(self, service):
        return not subprocess.call(["service", service, "reload"])

    # def _init_systemv_status_all(self):
    #     status_all = subprocess.call(["service", "--status-all"])
    #     for line in status_all:

    def list(self):
        if self.init_type == 1:
            return self._init_systemv_list()
        elif self.init_type == 2:
            return self._init_systemd_list()

    def status(self, service):
        if self.init_type == 1:
            return self._init_systemv_status(service)
        elif self.init_type == 2:
            return self._init_systemd_status(service)

    def start(self, service):
        if self.init_type == 1:
            return self._init_systemv_start(service)
        elif self.init_type == 2:
            return self._init_systemd_start(service)

    def stop(self, service):
        if self.init_type == 1:
            return self._init_systemv_stop(service)
        elif self.init_type == 2:
            return self._init_systemd_stop(service)

    def restart(self, service):
        if self.init_type == 1:
            return self._init_systemv_restart(service)
        elif self.init_type == 2:
            return self._init_systemd_restart(service)

    def reload(self, service):
        if self.init_type == 1:
            return self._init_systemv_reload(service)
        elif self.init_type == 2:
            return self._init_systemd_reload(service)