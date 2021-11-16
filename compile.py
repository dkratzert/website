import distutils.log
import distutils.dir_util
import os
import shutil
import sys
from collections import namedtuple
from contextlib import suppress
from datetime import datetime
from pathlib import Path

import markdown as markdown
import requests as requests
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


def shelxfile(template):
    markdown_content = Path(template.filename).read_text()
    return {"shelxfile_html": markdowner.convert(markdown_content)}


def render_md(site, template, **kwargs):
    # i.e. posts/post1.md -> build/posts/post1.html
    out = site.outpath / Path(template.name).with_suffix(".html")
    # Compile and stream the result
    os.makedirs(out.parent, exist_ok=True)
    site.get_template("shelxfile.html").stream(**kwargs).dump(str(out), encoding="utf-8")


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
    other1 = _get_executable(base_path, 'strf_cmd*.zip')
    files = _get_files_context(mac, suse, ubuntu, windows, other1=other1)
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


def _get_files_context(mac=Path(), suse=Path(), ubuntu=Path(), windows=Path(), other1=Path()):
    files = []
    item = namedtuple('item', 'name, date, system')
    if _is_there(windows):
        files.append(item(name=windows.name, date=_get_modified_date(windows), system='Windows 7 and up'))
    if _is_there(ubuntu):
        files.append(item(name=ubuntu.name, date=_get_modified_date(ubuntu), system='Ubuntu Linux 16'))
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
    dst_dir = Path(outpath).joinpath('files')
    print(dst_dir)
    #_copy_with_distutils(src_dir, dst_dir)
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


if __name__ == "__main__":
    if sys.platform == 'linux':
        os.system('git pull')
        outpath = '/var/www/html/'
    else:
        outpath = 'rendered'
    r = requests.get('https://raw.githubusercontent.com/dkratzert/ShelXFile/master/README.md')
    p = Path('dkratzert/templates/shelxfile.md')
    p.write_bytes(r.content)

    site = Site.make_site(searchpath='dkratzert/templates',
                          outpath=outpath,
                          contexts=[(r'.*\.html', base),
                                    ('structurefinder.html', structurefinder),
                                    ('dsr.html', dsr),
                                    ('finalcif.html', finalcif),
                                    (r".*\.md", shelxfile),
                                    ],
                          rules=[(r".*\.md", render_md)],
                          mergecontexts=True,
                          )
    copy_new_files_and_pics()
    # enable automatic reloading
    site.render(use_reloader=True)
