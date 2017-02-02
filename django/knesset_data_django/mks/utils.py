from knesset_data_django.mks.models import Member, Membership
from knesset_data_django.persons.models import Person, PersonAlias
import datetime

def get_all_mk_names():
    mks = []
    mk_names = []
    current_mks = Member.current_knesset.filter(is_current=True)
    mks.extend(current_mks)
    mk_names.extend(current_mks.values_list('name', flat=True))
    current_mk_ids = [m.id for m in current_mks]
    mk_persons = Person.objects.filter(
        mk__isnull=False,
        mk__id__in=current_mk_ids).select_related('mk')
    mk_aliases = PersonAlias.objects.filter(
        person__in=mk_persons).select_related('person', 'person__mk')
    mks.extend([person.mk for person in mk_persons])
    mk_names.extend(mk_persons.values_list('name', flat=True))
    mks.extend([alias.person.mk for alias in mk_aliases])
    mk_names.extend(mk_aliases.values_list('name', flat=True))
    return (mks, mk_names)


def party_at(member, date):
    """Returns the party this memeber was at given date
    """
    # make sure date is not a datetime object
    if isinstance(date, datetime.datetime):
        date = datetime.date(date.year, date.month, date.day)
    memberships = Membership.objects.filter(member=member).order_by('-start_date')
    for membership in memberships:
        if (not membership.start_date or membership.start_date <= date) and \
                (not membership.end_date or membership.end_date >= date):
            return membership.party
    return None
