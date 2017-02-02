# encoding: utf-8
from ...scrapers.committees import CommitteesScraper
from knesset_data_django.common.management_commands.base_no_args_command import BaseNoArgsCommand


class Command(BaseNoArgsCommand):
    help = "Fetch the all the committees information from the knesset and update existing"

    def handle_noargs(self, **options):
        super(Command, self).handle_noargs(**options)
        for committee, created in CommitteesScraper().scrape_active_committees():
            if created:
                self.logger.info(u"created committee {} - {}".format(committee.id, committee.name))
            else:
                self.logger.info(u'updated committee {} - {}'.format(committee.id, committee.name))
