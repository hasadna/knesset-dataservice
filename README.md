# knesset-data
[![travis-ci build status](https://travis-ci.org/hasadna/knesset-data.svg)](https://travis-ci.org/hasadna/knesset-data)

APIs and documentation to allow getting data about the Israeli Parliament (Knesset).

* [Issues](https://github.com/hasadna/knesset-dataservice/issues)
* [Contributing to knesset-data](CONTRIBUTING.md)

### Sub-projects

##### Data sources documentation

* [documentation about the Knesset data sources](docs/Data%20Sources.md)
* We also track Knesset datasources bugs and known problems - [see issues labeled "Knesset bug"](https://github.com/hasadna/knesset-data/issues?q=is%3Aissue+is%3Aopen+label%3A%22Knesset+bug%22)

##### Low level Python API

* Provides methods to fetch and parse Knesset data using Python.
* [python/README.md](python/README.md)
* Quickstart:
```
$ pip install knesset-data
python -c "from knesset_data.dataservice.committees import Committee\
print(', '.join([committee.name for committee in Committee.get_all_active_committees()]))
ועדת הכנסת, ועדת הכספים, ועדת הכלכלה, ועדת החוץ ...
```

##### Higher level Django module

* Store Knesset data in a structured DB and provides logic to handle the DB data.
* [django/README.md](django/README.md)
* Quickstart: see the [development guide](django/DEVELOPMENT.md)
