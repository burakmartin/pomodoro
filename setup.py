from setuptools import setup
import os

package_data = []
for root, dirs, files in os.walk('src/pomodoro/data/'):
    package_data += [
        os.path.join(root.replace('src/pomodoro/', ''), x) for x in files]

setup(
    version                 = "0.0.6",
    name                    = "Pomodoro",
    author                  = "Burak Martin",
    author_email            = "burak.martin100@gmail.com",
    url                     = "https://github.com/burakmartin/pomodoro",
    license_files           = "LICENSE",
    description             = "A small pomodoro GUI for Windows/Linux created with PyQt5.",
    license                 = "GPL-3.0-or-later",
    platforms               = "Windows, Linux",
    install_requires        = ["PyQt5 >= 5.15.0", "QDarkStyle>=2.8.1"],
    packages                = ['pomodoro'],
    package_dir             = {'' : 'src'},
    package_data            = {'pomodoro' : package_data},
    entry_points = {
    'console_scripts' : [
        'pomodoro = pomodoro.pomodoro:main',
        ]
    }
)
