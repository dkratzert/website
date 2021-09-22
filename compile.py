from staticjinja import Site


if __name__ == "__main__":
    site = Site.make_site(searchpath='dkratzert/templates', outpath='rendered')
    # enable automatic reloading
    site.render(use_reloader=True)