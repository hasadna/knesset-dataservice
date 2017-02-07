#!/usr/bin/env bash

host=${1:-oknesset-db1}

echo "Starting ssh socks proxy to ${host} (you can pass a different ssh host as first param)"
echo "Socks http proxy address: socks5://localhost:8123"
echo "To use with make_datapackage: bin/make_datapackage.py --http-proxy 'socks5://localhost:8123'"

ssh -D 8123 -C -N ${1:-oknesset-db1}
