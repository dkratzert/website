import datetime
import io
import pickle
import sys
from argparse import ArgumentParser
from contextlib import suppress
from pathlib import Path
from typing import Dict

from lars import apache

log_format = '%a - %u %t "%r" %>s %O "%{Referer}i" "%{User-agent}i"'
database_pickle_file = 'database.pickle'
counts_pickle = 'download_counts.pickle'


def get_logfile_rows(logfile, old_rows) -> dict:
    with io.open(logfile, 'r') as infile:
        with apache.ApacheSource(source=infile, log_format=log_format) as source:
            for row in source:
                if row.status != 200:
                    continue
                path = row.request.url.path_str
                if row.req_User_agent and 'bot' in row.req_User_agent \
                    or path == '/' \
                    or path.endswith('.html') \
                    or path.endswith('robots.txt') \
                    or path.endswith('mystats.txt') \
                    or path.endswith('.png') \
                    or path.endswith('.js') \
                    or path.endswith('.woff2') \
                    or path.endswith('.css'):
                    continue
                # print(row)
                # print(Path(path).name)
                old_rows[row.time] = (
                    row.remote_ip, row.request.url.path_str, row.bytes_sent, row.req_User_agent, row.status)
    return old_rows


def load_dumped_rows(filename):
    if Path(filename).exists():
        rows = load_rows()
    else:
        print('Pickled database not found!')
        sys.exit()
    return rows


def dump_rows(filename: str, rows: dict):
    with open(filename, 'wb') as f:
        pickle.dump(rows, f, pickle.HIGHEST_PROTOCOL)


def load_rows():
    with open(database_pickle_file, 'rb') as f:
        data = pickle.load(f)
    return data


def count_downloads(rows) -> Dict[str, int]:
    prog = {}
    # print(rows)
    for time, value in rows.items():
        with suppress(Exception):
            filename = Path(value[1]).name
            # print(filename)
            if filename == 'docs' or filename == 'favicon.ico':
                continue
            name = filename.split('-')[0].lower().split('-')[0]
            if name not in prog:
                prog[name] = 0
            prog[name] = prog[name] + 1
    return prog


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-l', '--log', help='Logfile to analyze', type=str)
    parser.add_argument('-f', '--force', help='Force, even if logfile is new', action='store_true', default=False)
    parser.add_argument('-p', '--print', help='Prints statistics', type=str)
    parser.add_argument('-d', '--dump', help='path to dump files', type=str)
    args = parser.parse_args()
    if not args.log:
        logfile = None
        parser.print_help()
        sys.exit()
    else:
        logfile = args.log
        if not Path(logfile).exists():
            print('Logfile {} not found.'.format(logfile))
            sys.exit()
        if not Path(database_pickle_file).exists() and args.force:
            previous_rows = {}
        else:
            previous_rows = load_dumped_rows(database_pickle_file)

    log_rows = get_logfile_rows(logfile, previous_rows)
    dump_rows(database_pickle_file, log_rows)
    # data = load_rows()
    # pprint(rows)
    print('---------------------------------')
    prog = count_downloads(log_rows)
    num_downloads = sum([x for x in prog.values()])
    num_downloads -= prog.get('version.txt', 0)
    print('\n\nNumber of downloads:', num_downloads)
    dump_rows(counts_pickle, prog)
    print('---------------------------------')
    prog = dict(sorted(prog.items(), key=lambda item: item[1], reverse=True))
    lines = []
    for key, val in prog.items():
        lines.append('{:>28}: {:<5}'.format(key, val))
    joined = '\n'.join(lines)
    print(joined)
    Path('./stats.txt').write_text('Start: 08.10.2021\n'
                                   'Number of downloads: {} -> {}\n--------------------------------\n'
                                   .format(num_downloads, datetime.datetime.now()) + joined)
