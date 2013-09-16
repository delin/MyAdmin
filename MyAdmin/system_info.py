import os

__author__ = 'delin'


class SystemInfo():
    def __init__(self):
        pass

    def get_load_avg(self):
        return os.getloadavg()

    def get_summary_info(self):
        uname = os.uname()
        os_name = uname[0]
        hostname = uname[1]
        kernel_version = uname[2]
        kernel_build = uname[3]
        kernel_arch = uname[4]

        return {
            'login': os.getlogin(),
            'uname': os.uname(),
            'os_name': os_name,
            'hostname': hostname,
            'kernel_version': kernel_version,
            'kernel_build': kernel_build,
            'kernel_arch': kernel_arch,
            'load_avg': os.getloadavg(),
        }