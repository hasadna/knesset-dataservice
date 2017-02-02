# encoding: utf-8
from knesset_data_django.common.management_commands.base_no_args_command import BaseNoArgsCommand
from optparse import make_option
import sys
import csv
from datetime import datetime
from knesset_data_django.committees.scrapers.members_attendance import MembersAttendanceScraper


BEGINNING_OF_CURRENT_KNESSET = u'תחילת כנסת נוכחית'
PERCENT_ATTENDANCE_FROM = u'אחוז נוכחות מ{}'
COMMITTEE = u'ועדה'
MK = u'ח"כ'


class Command(BaseNoArgsCommand):
    help = "Export members attendance data in csv format"

    option_list = BaseNoArgsCommand.option_list + (
        make_option('--from-date', dest='fromdate', default='', type=str,
                    help='get data from the given date (yyyy-mm-dd)'),
        make_option('--output-file', dest='outputfile', default='', type=str,
                    help='the output file name')
    )

    def handle_noargs(self, **options):
        super(Command, self).handle_noargs(**options)
        if options.get('outputfile', '') == '':
            out = sys.stdout
        else:
            out = open(options['outputfile'], 'wb')
        if 'fromdate' in options and options['fromdate'] != '':
            from_date = datetime.strptime(options['fromdate'], '%Y-%m-%d').date()
        else:
            from_date = None
        csvwriter = csv.writer(out)
        since_title = from_date.strftime('%d/%m/%Y') if from_date else BEGINNING_OF_CURRENT_KNESSET
        csvwriter.writerow([COMMITTEE.encode('utf-8'), MK.encode('utf-8'), (PERCENT_ATTENDANCE_FROM.format(since_title)).encode('utf-8')])
        for committee, members_attendance in MembersAttendanceScraper().scrape(from_date):
            self.logger.info('processing committee {}'.format(committee.id))
            for member, meetings_percentage in members_attendance:
                csvwriter.writerow([committee.name.encode('utf-8'), member.name.encode('utf-8'), member.meetings_percentage])
