# encoding: utf-8
from ....common.management_commands.base_no_args_command import BaseNoArgsCommand
from optparse import make_option
from django.utils.timezone import now, timedelta
from ...scrapers.committee_meetings import CommitteeMeetingsScraper


class Command(BaseNoArgsCommand):
    help = "Scrape latest committee meetings data from the knesset"

    option_list = BaseNoArgsCommand.option_list + (
        make_option('--from_days', dest='fromdays', default=5, type=int,
                    help="scrape meetings with dates from today minus X days"),
        make_option('--to_days', dest='todays', default=0, type=int,
                    help="scrape meetings with dates until today minus X days"),
        make_option('--committee-ids', dest='committeeids', default='', type=str,
                    help='comma-separated list of committee ids to iterate over (default=all committees)')
    )

    def _extract_cmd_args(self, from_days, to_days):
        from_date = now() - timedelta(days=from_days)
        to_date = now() - timedelta(days=to_days) if to_days else now()
        return from_date, to_date

    def handle_noargs(self, **options):
        super(Command, self).handle_noargs(**options)
        from_date, to_date = self._extract_cmd_args(options['fromdays'], options['todays'])
        committee_ids = options['committeeids'].split(',') if options['committeeids'] != '' else None
        self.logger.info('Scraping from {} to {}'.format(from_date, to_date))
        for committee, update_meeting_results in CommitteeMeetingsScraper().scrape(from_date, to_date, committee_ids):
            self.logger.info(u'Updating committee: {} ({})'.format(committee.name, committee.knesset_id))
            for dataservice_meeting, model_meeting, error in update_meeting_results:
                if model_meeting:
                    self.logger.info(u'updated meeting {}'.format(dataservice_meeting.id))
                else:
                    self.logger.info(u'error in meeting {}: {}'.format(dataservice_meeting.id, error))
