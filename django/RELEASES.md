# Knesset data django releases

#### Publishing a release to pypi

* merge some pull requests
* create a new draft release (https://github.com/hasadna/knesset-data/releases)
  * update the release notes, save draft
* edit [/django/setup.py](/django/setup.py)
  * update the version to match the version in the GitHub draft release
* publish the version to pypi
  * `knesset-data/django$ bin/update_pypi.sh`
* commit and push the version change
  * `knesset-data/python$ git commit -am "bump version to ..."`
  * `knesset-data/python$ git push hasadna master`
* publish the release on GitHub
* update release notes on GitHub release

#### Updating Open Knesset dependency

After publishing a release you probably want to update it in Open-Knesset

In Open Knesset repository -

* edit [Open-Knesset/requirements.txt](https://github.com/hasadna/Open-Knesset/blob/master/requirements.txt)
* `knesset-data==1.2.0`
* test and open a pull request in Open Knesset
