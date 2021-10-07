import io
import pickle
import sqlite3
from contextlib import suppress
from pathlib import Path
from pprint import pprint

from lars import apache

log_format = '%a - %u %t "%r" %>s %O "%{Referer}i" "%{User-agent}i"'

rows = {}

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
            #print(Path(path).name)
            with suppress(sqlite3.OperationalError):
                rows[row.time] = (row.remote_ip, row.request.url.path_str,
                                  row.bytes_sent, row.req_User_agent, row.status)

print(len(rows))

with open('database.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(rows, f, pickle.HIGHEST_PROTOCOL)

# geoip.init_databases(v4_geo_filename='')
# g = geoip.country_code_by_addr(IPv4Address('132.230.195.55'))
# print(g)

with open('database.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)

pprint(data)
