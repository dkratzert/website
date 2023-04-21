import os
import shutil
import sys
from collections import namedtuple
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Union

import markdown as markdown
import requests as requests
from jinja2 import Template
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from staticjinja import Site, staticjinja

markdowner = markdown.Markdown(output_format="html", extensions=[FencedCodeExtension(), CodeHiliteExtension()])


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
    """
    This method makes the html file available in the jinja2 context as 'name_htl'.
    So, there is only a tiny html file that displays the name_html context.

    {% extends '_base.html' %}
    <!-- The content of this file is directly converted from markdown -->
    {% block content %}
        {{ fragmentdb_html }}
    {% endblock content %}
    """
    markdown_path = Path(template.filename)
    if not markdown_path.with_suffix(".html").exists():
        print(f'Warning, you need to add a small templates/{markdown_path.with_suffix(".html").name} '
              f'file in order to make this to work:')
        print(md_to_html.__doc__)
        sys.exit()
    markdown_content = markdown_path.read_text()
    converted = markdowner.convert(markdown_content)
    return {markdown_path.stem + '_html': converted}


def render_md(site: 'Site', template: Template, **kwargs):
    # i.e. posts/post1.md -> build/posts/post1.html
    html_filename = Path(template.name).with_suffix(".html")
    out = site.outpath / html_filename
    # Compile and stream the result
    site.get_template(html_filename).stream(**kwargs).dump(str(out), encoding="utf-8")


def dsr(_: Template) -> dict:
    context = {}
    base_path = Path('./files/dsr')
    windows = _get_executable(base_path, 'DSR-setup*.exe')
    windows7 = _get_executable(base_path, 'DSR-setup-win7*.exe')
    ubuntu = _get_executable(base_path, 'dsr*.deb')
    suse = _get_executable(base_path, 'DSR*.rpm')
    mac = _get_executable(base_path, 'DSR*.dmg')
    files = _get_files_context(mac, suse, ubuntu, windows, windows7=windows7, windows_version=10)
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
    files = _get_files_context(mac, suse, ubuntu, windows, other1=zip_file,
                               ubuntu_version=20, windows_version=10)
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
    windows = _get_executable(base_path, 'FinalCif-setup-x64-*.exe')
    windows7 = _get_executable(base_path, 'FinalCif-setup-x64_win7*.exe')
    ubuntu = _get_executable(base_path, 'FinalCif*ubuntu')
    suse = _get_executable(base_path, 'FinalCif*opensuse')
    mac = _get_executable(base_path, 'Finalcif*macos.app.zip')
    files = _get_files_context(mac, suse, ubuntu, windows, windows7=windows7,
                               ubuntu_version=20,
                               windows_version=10)
    context.update(
        {'version'  : _get_version_number(base_path),
         'link_base': base_path,
         'files'    : files
         }
    )
    print('Rendering FinalCif')
    return context


def _get_files_context(mac=Path(), suse=Path(), ubuntu=Path(), windows=Path(), other1=Path(), windows7=Path(),
                       ubuntu_version=16,
                       windows_version=7):
    files = []
    item = namedtuple('item', 'name, date, system')
    if _is_there(windows):
        files.append(
            item(name=windows.name, date=_get_modified_date(windows), system=f'Windows {windows_version} and up'))
    if _is_there(windows7):
        files.append(
            item(name=windows7.name, date=_get_modified_date(windows7), system=f'Windows 7 and up'))
    if _is_there(ubuntu):
        files.append(
            item(name=ubuntu.name, date=_get_modified_date(ubuntu), system=f'Ubuntu Linux {ubuntu_version}'))
    if _is_there(suse):
        files.append(item(name=suse.name, date=_get_modified_date(suse), system='OpenSuSE Linux 15.2'))
    if _is_there(mac):
        files.append(item(name=mac.name, date=_get_modified_date(mac), system='MacOS 11.6'))
    if _is_there(other1):
        files.append(item(name=other1.name, date=_get_modified_date(other1), system='Web Interface'))
    return files


def copy_new_files_and_pics(outpath):
    # Copy pictures:
    print('---> Copy pictures and files to', Path(outpath).resolve())
    _copy_with_rsync(src_dir=Path('./dkratzert/pictures'), dst_dir=Path(outpath).joinpath('pictures'))
    # Copy files verbose:
    src_dir = Path('./dkratzert/files')
    dst_dir = Path(outpath)
    print('Syncing {} with rsync into {}'.format(src_dir, dst_dir))
    print('\n-> Copy executables:')
    _copy_with_rsync(src_dir, dst_dir)
    try:
        shutil.copy2('./dkratzert/pictures/favicon.png', Path(outpath))
        shutil.copy2('./dkratzert/pictures/favicon.ico', Path(outpath))
    except FileNotFoundError:
        print('\nWarning!! Favicons not found! -------------------------------\n')
    with suppress(Exception):
        shutil.copy2(list(Path('../').glob('google*.html'))[0], Path(outpath))
    print('------------')


def _copy_with_rsync(src_dir: Union[str, Path], dst_dir: Union[str, Path]) -> None:
    os.system('rsync -rumv --delete-after {} {}'.format(src_dir, dst_dir))


def get_shelxfile_readme():
    r = requests.get('https://raw.githubusercontent.com/dkratzert/ShelXFile/master/README.md')
    shelxfile_path = Path('dkratzert/templates/shelxfile.md')
    shelxfile_path.write_bytes(r.content)


def get_fragmentdb_readme():
    r = requests.get('https://raw.githubusercontent.com/dkratzert/FragmentDB/master/help/fragmentdb.md')
    fragmentdb_path = Path('dkratzert/templates/fragmentdb.md')
    fragmentdb_path.write_bytes(r.content)


def get_finalcif_changelog():
    r = requests.get('https://raw.githubusercontent.com/dkratzert/FinalCif/master/docs/changelog.txt')
    changelog_path = Path('dkratzert/templates/fcchangelog.md')
    changelog_path.write_bytes(r.content)


def get_strf_changelog():
    r = requests.get('https://raw.githubusercontent.com/dkratzert/StructureFinder/master/docs/changes.txt')
    changelog_path = Path('dkratzert/templates/strfchangelog.md')
    changelog_path.write_bytes(r.content)

def get_dsr_changelog():
    r = requests.get('https://raw.githubusercontent.com/dkratzert/DSR/master/setup/Output/changelog.txt')
    changelog_path = Path('dkratzert/templates/dsrchangelog.md')
    changelog_path.write_bytes(r.content)


if __name__ == "__main__":
    if sys.platform == 'linux':
        os.system('git pull')
        outpath = '/var/www/html/'
    else:
        outpath = 'rendered'

    get_fragmentdb_readme()
    get_shelxfile_readme()
    get_finalcif_changelog()
    get_strf_changelog()
    get_dsr_changelog()

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
    copy_new_files_and_pics(outpath)
    # enable automatic reloading
    #site.render(use_reloader=True)
    site.render()
