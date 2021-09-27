import os
import shutil
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
    return list(base_path.glob(pattern))[0]


def dsr(template):
    base_path = Path('./files/dsr')
    windows = _get_executable(base_path, 'dsr-setup*.exe')
    ubuntu = _get_executable(base_path, 'dsr*.deb')
    suse = _get_executable(base_path, 'dsr*.rpm')
    mac = _get_executable(base_path, 'DSR*.dmg')
    version = _get_executable(base_path, 'version.txt').read_text()
    return {
        'windows_name': windows,
        'windows_date': _get_modified_date(windows),
        'ubuntu_name' : ubuntu,
        'ubuntu_date' : _get_modified_date(ubuntu),
        'suse_name'   : suse,
        'suse_date'   : _get_modified_date(suse),
        'mac_name'    : mac,
        'mac_date'    : _get_modified_date(mac),
        'version': version
    }


def structurefinder(template):
    base_path = Path('./files/structurefinder')
    windows = _get_executable(base_path, 'StructureFinder*.exe')
    ubuntu = _get_executable(base_path, 'StructureFinder*_ubuntu')
    suse = _get_executable(base_path, 'StructureFinder*_opensuse')
    version = _get_executable(base_path, 'version.txt').read_text()
    return {
        'windows_name': windows,
        'windows_date': _get_modified_date(windows),
        'ubuntu_name' : ubuntu,
        'ubuntu_date' : _get_modified_date(ubuntu),
        'suse_name'   : suse,
        'suse_date'   : _get_modified_date(suse),
        # 'mac_name'    : 'StructureFinder-setup-x64-v55.exe',
        # 'mac_date'    : '2021-05-04',,
        'version': version
    }


def finalcif(template):
    base_path = Path('./files/finalcif')
    windows = _get_executable(base_path, 'FinalCif-setup-x64*.exe')
    ubuntu = _get_executable(base_path, 'FinalCif*ubuntu')
    suse = _get_executable(base_path, 'FinalCif*opensuse')
    mac = _get_executable(base_path, 'Finalcif*macos.app.zip')
    version = _get_executable(base_path, 'version.txt').read_text()
    return {
        'windows_name': windows,
        'windows_date': _get_modified_date(windows),
        'ubuntu_name' : ubuntu,
        'ubuntu_date' : _get_modified_date(ubuntu),
        'suse_name'   : suse,
        'suse_date'   : _get_modified_date(suse),
        'mac_name'    : mac,
        'mac_date'    : _get_modified_date(mac),
        'version'     : version
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
                          # mergecontexts=True,
                          )
    print(Path('.').resolve())
    shutil.copytree(Path('../pictures'), Path(outpath).joinpath('pictures'), dirs_exist_ok=True)
    shutil.copytree(Path('../files'), Path(outpath).joinpath('files'), dirs_exist_ok=True)

    # enable automatic reloading
    site.render(use_reloader=True)
