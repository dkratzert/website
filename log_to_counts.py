import io
import pickle
import sqlite3
from contextlib import suppress
from pathlib import Path

from lars import apache

log_format = '%a - %u %t "%r" %>s %O "%{Referer}i" "%{User-agent}i"'
database_pickle = 'database.pickle'
counts_pickle = 'download_counts.pickle'


def get_logfile_rows() -> dict:
    rows = load_dumped_rows(database_pickle)
    with io.open('/Users/daniel/Documents/access2.log', 'r') as infile:
        with apache.ApacheSource(source=infile, log_format=log_format) as source:
            for row in source:
                if row.status != 200:
                    continue
                path = row.request.url.path_str
                if row.req_User_agent and 'bot' in row.req_User_agent \
                    or path == '/' \
                    or path.endswith('.html') \
                    or path.endswith('.txt') \
                    or path.endswith('.png') \
                    or path.endswith('.js') \
                    or path.endswith('.woff2') \
                    or path.endswith('.css'):
                    continue
                # print(row)
                # print(Path(path).name)
                with suppress(sqlite3.OperationalError):
                    rows[row.time] = (row.remote_ip, row.request.url.path_str,
                                      row.bytes_sent, row.req_User_agent, row.status)
    return rows


def load_dumped_rows(filename):
    if Path(filename).exists():
        rows = load_rows()
    else:
        rows = {}
    return rows


def dump_rows(filename: str, rows: dict):
    with open(filename, 'wb') as f:
        pickle.dump(rows, f, pickle.HIGHEST_PROTOCOL)


def load_rows():
    with open(database_pickle, 'rb') as f:
        data = pickle.load(f)
    return data


def count_downloads(rows):
    prog = {}
    for time, value in rows.items():
        with suppress(Exception):
            filename = Path(value[1]).name
            if filename == 'docs':
                continue
            name = filename.split('-')[0].lower().split('-')[0]
            if name not in prog:
                prog[name] = 0
            prog[name] = prog[name] + 1
    return prog


if __name__ == '__main__':
    rows = get_logfile_rows()
    dump_rows(database_pickle, rows)
    # data = load_rows()
    # pprint(rows)
    print('Number of downloads:', len(rows))
    prog = count_downloads(rows)
    print(prog)
    dump_rows(counts_pickle, prog)
