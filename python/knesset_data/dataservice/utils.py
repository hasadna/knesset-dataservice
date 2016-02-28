import requests


def compose_url_get(url, params):
    p = requests.PreparedRequest()
    p.prepare(method='GET', url=url, params=params)
    return p.url
