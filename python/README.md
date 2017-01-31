knesset-data
============

A python module that provides api to available Israeli Parliament (Knesset) data

### Installation
* $ pip install knesset-data

### Usage Example
* $ python
* >>> from knesset_data.dataservice.committees import Committee
* >>> committees = Committee.get_all_active_committees()
* >>> len(committees)
* 19
* >>> print committees[0].name
* ועדת הכנסת

### Using ssh socks proxy - to overcome knesset ip blocks

Knesset blocks ips that try to scrape from it.

You can use an ssh socks proxy to route scraping traffic via open knesset scraping server (if you have ssh access to it)

Assuming you have ssh host "oknesset-db1" configured, you can do this:

```
python$ bin/ssh_socks_proxy.sh oknesset-db1
```

Then, you can make a datapackage using:

```
python$ bin/make_datapackage.py --http-proxy socks5://localhost:8123
```

### Project Administration

#### Publishing a release to pypi

* merge some pull requests
* create a new draft release (https://github.com/hasadna/knesset-data/releases)
  * update the release notes, save draft
* edit [/python/setup.py](/python/setup.py)
  * update the version to match the version in the GitHub draft release
* publish the version to pypi
  * `$ cd knesset-data/python`
  * `knesset-data/python$ bin/update_pypi.sh`
* commit and push the version change
  * `knesset-data/python$ git commit -am "bump version to ..."`
  * `knesset-data/python$ git push hasadna master`
* publish the release on GitHub

#### Updating Open Knesset dependency

After publishing a release you probably want to update it in Open-Knesset

In Open Knesset repository -

* edit [Open-Knesset/requirements.txt](https://github.com/hasadna/Open-Knesset/blob/master/requirements.txt)
* `knesset-data==1.2.0`
* test and open a pull request in Open Knesset
