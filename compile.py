import datetime
import os
import shutil
from pathlib import Path

from staticjinja import Site


def base(template):
    template_mtime = os.path.getmtime(template.filename)
    date = datetime.datetime.fromtimestamp(template_mtime)
    return {
        'template_date': date.strftime('%d %B %Y'),
        'title'        : 'MySite',
    }


def index(template):
    return {'title': 'MySite - Index'}


def structurefinder(template):
    return {
        # TODO: Fill this list automatically
        'windows_name': 'StructureFinder-setup-x64-v55.exe',
        'ubuntu_name' : 'StructureFinder-setup-x64-v55.exe',
        'suse_name'   : 'StructureFinder-setup-x64-v55.exe',
        'mac_name'    : 'StructureFinder-setup-x64-v55.exe',
        'windows_date': '2021-05-04',
        'ubuntu_date' : '2021-05-04',
        'suse_date'   : '2021-05-04',
        'mac_date'    : '2021-05-04',
        'windows_link': '/foo/bar/strf.exe',
    }


def dsr(template):
    return {
        'windows_name': 'StructureFinder-setup-x64-v55.exe',
        'ubuntu_name' : 'StructureFinder-setup-x64-v55.exe',
        'suse_name'   : 'StructureFinder-setup-x64-v55.exe',
        'mac_name'    : 'StructureFinder-setup-x64-v55.exe',
        'windows_date': '2021-05-04',
        'ubuntu_date' : '2021-05-04',
        'suse_date'   : '2021-05-04',
        'mac_date'    : '2021-05-04',
    }


def finalcif(template):
    return {
        'windows_name': 'StructureFinder-setup-x64-v55.exe',
        'ubuntu_name' : 'StructureFinder-setup-x64-v55.exe',
        'suse_name'   : 'StructureFinder-setup-x64-v55.exe',
        'mac_name'    : 'StructureFinder-setup-x64-v55.exe',
        'windows_date': '2021-05-04',
        'ubuntu_date' : '2021-05-04',
        'suse_date'   : '2021-05-04',
        'mac_date'    : '2021-05-04',
    }


if __name__ == "__main__":
    outpath = 'rendered'
    site = Site.make_site(searchpath='dkratzert/templates',
                          outpath=outpath,
                          contexts=[('.*.html', base),
                                    ('index.html', index),
                                    ('structurefinder.html', structurefinder),
                                    ('dsr.html', dsr),
                                    ('finalcif.html', finalcif),
                                    ],
                          mergecontexts=True,
                          )
    print(Path('.').resolve())
    shutil.copytree(Path('../pictures'), Path(outpath).joinpath('pictures'), dirs_exist_ok=True)
    shutil.copytree(Path('../files'), Path(outpath).joinpath('files'), dirs_exist_ok=True)

    # enable automatic reloading
    site.render(use_reloader=True)

