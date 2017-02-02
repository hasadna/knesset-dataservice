from datetime import date
from ..mks.models import Knesset, Member
from django.db.models.query_utils import Q


def members_extended(committee, current_only=False, ids=None):
    '''
    a queryset of Members who are part of the committee, as members,
    chairpersons or replacements.
    '''
    query = Q(committees=committee) | Q(chaired_committees=committee) | Q(
        replacing_in_committees=committee)
    qs = Member.objects.filter(query).distinct()
    if ids is not None:
        return qs.filter(id__in=ids)
    elif current_only:
        return qs.filter(is_current=True)
    else:
        return qs


def members_by_presence(committee, ids=None, from_date=None, current_only=False):
    """Returns a list of members with computed presence percentage.
    If ids is not provided, this will return committee members. if ids is
    provided, this will return presence data for the given members.
    """
    members = members_extended(committee, current_only, ids)

    if from_date is not None:
        include_this_year = False
    else:
        # this is compatibility mode to support existing views
        include_this_year = True

    def count_percentage(res_set, total_count):
        return (100 * res_set.count() / total_count) if total_count else 0

    def filter_this_year(res_set):
        year_start = date.today().replace(month=1, day=1)
        return res_set.filter(date__gte=year_start)

    d = Knesset.objects.current_knesset().start_date if from_date is None else from_date
    meetings_with_mks = committee.meetings.filter(mks_attended__isnull=False).distinct()
    all_meet_count = meetings_with_mks.filter(date__gte=d).count()
    year_meet_count = filter_this_year(meetings_with_mks).count() if include_this_year else None
    for m in members:
        all_member_meetings = m.committee_meetings.filter(committee=committee, date__gte=d)
        m.meetings_percentage = count_percentage(all_member_meetings, all_meet_count)
        if include_this_year:
            year_member_meetings = filter_this_year(all_member_meetings)
            m.meetings_percentage_year = count_percentage(year_member_meetings, year_meet_count)
    return sorted(members, key=lambda x: x.meetings_percentage, reverse=True)
