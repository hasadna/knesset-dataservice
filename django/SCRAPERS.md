# kneseset-data-django scrapers guide

**Important** Please be sure to read and understand this document before working on scrapers.
We know from (bitter?) experience that scrapers will always require changes.
That's why it's important to keep the scrapers in this project in high quality to allow maintanence and changes in the future.

**Thank you for your cooperation!**

### Scraper objects

Each scraper should have a scraper object.

This is an object that extends [common.scrapers.base_scraper.BaseScraper](knesset_data_django/common/scrapers/base_scraper.py)

##### Guidelines

* Scraper objects should output machine readable data about the scraping work that was done.
* Ideally it would be a generator - to allow streaming
  * But, it can also be statistical data (e.g. summary of how many objects were updated / processed).
* The important thing is that the main output of the scraper is machine readable data and not textual output.
* All external dependencies (e.g. http requests) should be inside an overridable function - to allow automated testing

##### Examples

* [committees.scrapers.committees.CommitteesScraper](knesset_data_django/committees/scrapers/committees.py)
* [committees.scrapers.committee_meetings.CommitteeMeetingsScraper](knesset_data_django/committees/scrapers/committee_meetings.py)


## Scraper Unit/functional tests

Each scraper must have a corresponding test.

Tests are django test cases and can use the test DB.

##### Guidelines

* Tests should be easy to update -
  * should have clear input and expected output
  * should use reusable functions with clear input / output as much as possible

##### Examples
* [committees.scrapers.tests.test_committee_meetings.CommitteeMeetingsScraperTestCase](knesset_data_django/committees/scrapers/tests/test_committee_meetings.py)
* [committees.scrapers.tests.test_committees.CommitteesScraperTestCase](knesset_data_django/committees/scrapers/tests/test_committees.py)

### Management commands

Management commands are the way we run the scrapers.

Management commands should extend [BaseNoArgsCommand](knesset_data_django/common/management_commands/base_no_args_command.py).

##### Guildelines

* A management command should have minimal logic and just call the relevant scraper.
* It is just a human interface to the scraper.
* It handles getting input about what scraping to do and outputs human readable output.

##### Examples

* [committees.management.commands.scrape_committees](knesset_data_django/committees/management/commands/scrape_committees.py)

## See also

* [Development guide](DEVELOPMENT.md)
