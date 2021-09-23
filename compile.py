import datetime
import os

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
    return {'strf_windows_name'     : 'StructureFinder-setup-x64-v55.exe',
            'strf_windows_date': '2021-05-04',
            'strf_windows_link': '/foo/bar/strf.exe',
            }


if __name__ == "__main__":
    site = Site.make_site(searchpath='dkratzert/templates',
                          outpath='rendered',
                          contexts=[('.*.html', base),
                                    ('index.html', index),
                                    ('structurefinder.html', structurefinder)],
                          mergecontexts=True,
                          )
    # enable automatic reloading
    site.render(use_reloader=True)
