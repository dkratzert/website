import distutils.dir_util
import distutils.log
import os
import shutil
import sys
from collections import namedtuple
from contextlib import suppress
from datetime import datetime
from pathlib import Path

import markdown as markdown
import requests as requests
from jinja2 import Template
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from staticjinja import Site

# noinspection PyTypeChecker
markdowner = markdown.Markdown(output_format="html5", extensions=[FencedCodeExtension(), CodeHiliteExtension()])


def base(template):
    template_mtime = os.path.getmtime(template.filename)
    date = datetime.fromtimestamp(template_mtime)
    return {
        'template_date': date.strftime('%Y-%m-%d'),
        'title'        : 'Daniel Kratzerts SC-XRD tools',
    }


def _get_modified_date(os_path: Path) -> str:
    return datetime.fromtimestamp(os_path.stat().st_mtime).strftime('%Y-%m-%d')


def _get_executable(base_path: Path, pattern: str) -> Path:
    paths = list(Path(outpath).joinpath(base_path).glob(pattern))
    return paths[0] if paths else Path()


def _is_there(file):
    return file.is_file() and file.exists()


def _get_version_number(base_path):
    version_txt = _get_executable(base_path, 'version.txt')
    if version_txt.exists() and version_txt.is_file():
        return version_txt.read_text()
    else:
        return '0'


def md_to_html(template: Template):
    markdown_content = Path(template.filename).read_text()
    return {str(Path(template.name).stem) + '_html': markdowner.convert(markdown_content)}


def render_md(site, template: Template, **kwargs):
    # i.e. posts/post1.md -> build/posts/post1.html
    filename = Path(template.name).with_suffix(".html")
    out = site.outpath / filename
    # Compile and stream the result
    os.makedirs(out.parent, exist_ok=True)
    site.get_template(filename).stream(**kwargs).dump(str(out), encoding="utf-8")


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
    print('Rendering DSR')
    return context


def structurefinder(template):
    context = {}
    base_path = Path('./files/structurefinder/')
    windows = _get_executable(base_path, 'StructureFinder-*.exe')
    ubuntu = _get_executable(base_path, 'StructureFinder*_ubuntu')
    suse = _get_executable(base_path, 'StructureFinder*_opensuse')
    mac = _get_executable(base_path, 'StructureFinder*macos.app.zip')
    zip_file = _get_executable(base_path, 'strf_cmd*.zip')
    files = _get_files_context(mac, suse, ubuntu, windows, other1=zip_file, ubuntu_version=18)
    context.update(
        {'version'  : _get_version_number(base_path),
         'link_base': base_path,
         'files'    : files
         })
    print('Rendering StructureFinder')
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
    print('Rendering FinalCif')
    return context


def _get_files_context(mac=Path(), suse=Path(), ubuntu=Path(), windows=Path(), other1=Path(), ubuntu_version=16):
    files = []
    item = namedtuple('item', 'name, date, system')
    if _is_there(windows):
        files.append(item(name=windows.name, date=_get_modified_date(windows), system='Windows 7 and up'))
    if _is_there(ubuntu):
        files.append(
            item(name=ubuntu.name, date=_get_modified_date(ubuntu), system='Ubuntu Linux {}'.format(ubuntu_version)))
    if _is_there(suse):
        files.append(item(name=suse.name, date=_get_modified_date(suse), system='OpenSuSE Linux 15.2'))
    if _is_there(mac):
        files.append(item(name=mac.name, date=_get_modified_date(mac), system='MacOS 11.6'))
    if _is_there(other1):
        files.append(item(name=other1.name, date=_get_modified_date(other1), system='Web Interface'))
    return files


def copy_new_files_and_pics():
    # Copy pictures:
    print('---> Copy pictures and files to', outpath)
    _copy_with_distutils(src_dir=Path('./dkratzert/pictures'), dst_dir=Path(outpath).joinpath('pictures'))
    # Copy files verbose:
    src_dir = Path('./dkratzert/files')
    dst_dir = Path(outpath)
    print('Syncing {} with rsync into {}'.format(src_dir, dst_dir))
    print('\n-> Copy executables:')
    os.system('rsync -rumv --delete-after {} {}'.format(src_dir, dst_dir))
    shutil.copy2('./dkratzert/pictures/favicon.png', Path(outpath))
    shutil.copy2('./dkratzert/pictures/favicon.ico', Path(outpath))
    with suppress(Exception):
        shutil.copy2(list(Path('../').glob('google*.html'))[0], Path(outpath))
    print('------------')


def _copy_with_distutils(src_dir, dst_dir):
    shutil.rmtree(dst_dir, ignore_errors=True)
    distutils.log.set_verbosity(distutils.log.DEBUG)
    distutils.dir_util.copy_tree(
        str(src_dir),
        str(dst_dir),
        update=1,
        verbose=1,
    )


def get_shelxfile_readme():
    r = requests.get('https://raw.githubusercontent.com/dkratzert/ShelXFile/master/README.md')
    shelxfile_path = Path('dkratzert/templates/shelxfile.md')
    shelxfile_path.write_bytes(r.content)


def get_finalcif_changelog():
    r = requests.get('https://raw.githubusercontent.com/dkratzert/FinalCif/master/docs/changelog.txt')
    changelog_path = Path('dkratzert/templates/fcchangelog.md')
    changelog_path.write_bytes(r.content)


if __name__ == "__main__":
    if sys.platform == 'linux':
        os.system('git pull')
        outpath = '/var/www/html/'
    else:
        outpath = 'rendered'

    get_shelxfile_readme()
    get_finalcif_changelog()

    site = Site.make_site(searchpath='dkratzert/templates',
                          outpath=outpath,
                          contexts=[(r'.*\.html', base),
                                    ('structurefinder.html', structurefinder),
                                    ('dsr.html', dsr),
                                    ('finalcif.html', finalcif),
                                    (r".*\.md", md_to_html),
                                    ],
                          rules=[(r".*\.md", render_md)],
                          mergecontexts=True,
                          )
    copy_new_files_and_pics()
    # enable automatic reloading
    site.render(use_reloader=True)
