import os
import shutil
import sys
from collections import namedtuple
from datetime import datetime
from pathlib import Path

from staticjinja import Site


def base(template):
    template_mtime = os.path.getmtime(template.filename)
    date = datetime.fromtimestamp(template_mtime)
    return {
        'template_date': date.strftime('%Y-%m-%d'),
        'title'        : 'MySite',
    }


def index(template):
    return {'title': 'MySite - Index'}


def _get_modified_date(os_path: Path) -> str:
    return datetime.fromtimestamp(os_path.stat().st_mtime).strftime('%Y-%m-%d')


def _get_executable(base_path: Path, pattern: str) -> Path:
    paths = list(base_path.glob(pattern))
    return paths[0] if paths else Path()


def _is_there(file):
    return file.is_file() and file.exists()


def _get_version_number(base_path):
    version_txt = _get_executable(base_path, 'version.txt')
    if version_txt.exists() and version_txt.is_file():
        return version_txt.read_text()
    else:
        return '0'


def dsr(template):
    context = {}
    base_path = Path('./files/dsr')
    windows = _get_executable(base_path, 'DSR-setup*.exe')
    ubuntu = _get_executable(base_path, 'dsr*.deb')
    suse = _get_executable(base_path, 'DSR*.rpm')
    mac = _get_executable(base_path, 'DSR*.dmg')
    files = _get_files_context(mac, suse, ubuntu, windows)
    context.update(
        {'version'  : _get_version_number(base_path),
         'link_base': base_path,
         'files'    : files
         }
    )
    return context


def structurefinder(template):
    context = {}
    base_path = Path('./files/structurefinder/')
    windows = _get_executable(base_path, 'StructureFinder-*.exe')
    ubuntu = _get_executable(base_path, 'StructureFinder*_ubuntu')
    suse = _get_executable(base_path, 'StructureFinder*_opensuse')
    mac = _get_executable(base_path, 'StructureFinder*macos.app.zip')
    other1 = _get_executable(base_path, 'strf_cmd*.zip')
    # print(base_path, windows, '###')
    files = _get_files_context(mac, suse, ubuntu, windows, other1=other1)
    context.update(
        {'version'  : _get_version_number(base_path),
         'link_base': base_path,
         'files'    : files
         })
    return context


def finalcif(template):
    context = {}
    base_path = Path('./files/finalcif')
    windows = _get_executable(base_path, 'FinalCif-setup-x64*.exe')
    ubuntu = _get_executable(base_path, 'FinalCif*ubuntu')
    suse = _get_executable(base_path, 'FinalCif*opensuse')
    mac = _get_executable(base_path, 'Finalcif*macos.app.zip')
    files = _get_files_context(mac, suse, ubuntu, windows)
    context.update(
        {'version'  : _get_version_number(base_path),
         'link_base': base_path,
         'files'    : files
         }
    )
    return context


def _get_files_context(mac=Path(), suse=Path(), ubuntu=Path(), windows=Path(), other1=Path()):
    files = []
    item = namedtuple('item', 'name, date, system')
    if _is_there(windows):
        files.append(item(name=windows.name, date=_get_modified_date(windows), system='Windows'))
    if _is_there(ubuntu):
        files.append(item(name=ubuntu.name, date=_get_modified_date(ubuntu), system='Ubuntu Linux'))
    if _is_there(suse):
        files.append(item(name=suse.name, date=_get_modified_date(suse), system='OpenSuSE Linux'))
    if _is_there(mac):
        files.append(item(name=mac.name, date=_get_modified_date(mac), system='MacOS'))
    if _is_there(other1):
        files.append(item(name=other1.name, date=_get_modified_date(other1), system='Web Interface'))
    return files


if __name__ == "__main__":
    if  sys.platform == 'linux':
        outpath = '/var/www/html/rendered'
    else:
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
    print('---> copy files to', outpath)
    p = shutil.copytree(Path('./pictures'), Path(outpath).joinpath('pictures'), dirs_exist_ok=True)
    print(p)
    p = shutil.copytree(Path('./files'), Path(outpath).joinpath('files'), dirs_exist_ok=True)
    print(p)
    print('------------')
    # enable automatic reloading
    site.render(use_reloader=True)
