from http.server import BaseHTTPRequestHandler
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()
        self.wfile.write("\n")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        estacion = parse_qs(urlparse(self.path).query).get('estacion')[0]
        date = parse_qs(urlparse(self.path).query).get('date')[0]
        data = {'menu':  'consulta', 'smenu': 'reports', 'link': 'data',
                'view': 'data', 'magnitud': '', 'estacion': int(estacion),
                'date': date}
        url = 'http://www.mambiente.munimadrid.es/sica/scripts/index.php?lang=es'
        r = requests.post(url, data=data)
        soup = BeautifulSoup(r.content, 'html.parser')
        tables = soup.find_all('table')
        table = tables[4]
        meta = table.find_all(class_='hs')
        headers = table.find_all(class_='hd')
        tmp = dict()
        data = table.find_all(class_='datos')
        val = []
        for i in range(len(headers)):
            val.append(list())
        for idx, d in enumerate(data):
            k = idx % len(headers)
            v = d.get_text()
            if ((':' not in v) and ('-' not in v)):
                v = float(v)
            else:
                if ('-' in v):
                    v = -1.0
            val[k].append(v)
        for idx, h in enumerate(headers):
            k = idx % len(headers)
            v = h.get_text()
            tmp[v] = val[k]
        tmp['estacion'] = meta[0].get_text()
        tmp['fecha'] = meta[1].get_text()
        self.wfile.write(str(json.dumps(tmp)).encode())
