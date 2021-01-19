from setuptools import setup
import os

package_data = []

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

for root, dirs, files in os.walk('src/pomodoro/data/'):
    package_data += [
        os.path.join(root.replace('src/pomodoro/', ''), x) for x in files]

setup(
    version                       = "0.0.7",
    name                          = "pomodoro-gui",
    author                        = "Burak Martin",
    author_email                  = "burak.martin100@gmail.com",
    url                           = "https://github.com/burakmartin/pomodoro",
    license_files                 = "LICENSE",
    description                   = "A small pomodoro GUI for Windows/Linux created with PyQt5.",
    long_description              = long_description,
    long_description_content_type = "text/markdown", 
    license                       = "GPL-3.0-or-later",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires               = '>=3.5', 
    install_requires              = ["PyQt5 >= 5.15.0", "QDarkStyle>=2.8.1"],
    packages                      = ['pomodoro'],
    package_dir                   = {'' : 'src'},
    package_data                  = {'pomodoro' : package_data},
    entry_points                  = {
        'console_scripts' : [
            'pomodoro = pomodoro.pomodoro:main',
            ]
    }
)
