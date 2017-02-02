from knesset_data.protocols.committee import CommitteeMeetingProtocol
from datetime import datetime
import logging
import subprocess
import os
import urllib
from knesset_data_django.mks.utils import get_all_mk_names, party_at
from django.core.exceptions import ValidationError
from .plenum_protocol_parts import create_plenum_protocol_parts
from django.conf import settings
from ..committees.models import Committee, CommitteeMeeting, ProtocolPart
from annotatetext.models import Annotation
from django.contrib.contenttypes.models import ContentType


logger = logging.getLogger(__name__)


def redownload_protocol(committee_meeting):
    if committee_meeting.committee.type == 'plenum':
        download_for_existing_meeting(committee_meeting)
    else:
        with CommitteeMeetingProtocol.get_from_url(committee_meeting.src_url) as protocol:
            committee_meeting.protocol_text = protocol.text
            committee_meeting.protocol_text_update_date = datetime.now()
            committee_meeting.save()


def create_protocol_parts(committee_meeting, delete_existing=False, mks=None, mk_names=None):
    """ Create protocol parts from this instance's protocol_text
        Optionally, delete existing parts.
        If the meeting already has parts, and you don't ask to
        delete them, a ValidationError will be thrown, because
        it doesn't make sense to create the parts again.
    """
    logger.debug('create_protocol_parts %s' % delete_existing)
    if delete_existing:
        ppct = ContentType.objects.get_for_model(ProtocolPart)
        annotations = Annotation.objects.filter(content_type=ppct,
                                                object_id__in=committee_meeting.parts.all)
        logger.debug(
            'deleting %d annotations, because I was asked to delete the relevant protocol parts on cm.id=%d' % (
                annotations.count(), committee_meeting.id))
        annotations.delete()
        committee_meeting.parts.all().delete()
    else:
        if committee_meeting.parts.count():
            raise ValidationError(
                'CommitteeMeeting already has parts. delete them if you want to run create_protocol_parts again.')
    if not committee_meeting.protocol_text:  # sometimes there are empty protocols
        return  # then we don't need to do anything here.
    if committee_meeting.committee.type == 'plenum':
        create_plenum_protocol_parts(committee_meeting, mks=mks, mk_names=mk_names)
        return
    else:
        def get_protocol_part(i, part):
            logger.debug('creating protocol part %s' % i)
            return ProtocolPart(meeting=committee_meeting, order=i, header=part.header,
                                body=part.body)
        with CommitteeMeetingProtocol.get_from_text(
                committee_meeting.protocol_text) as protocol:
            ProtocolPart.objects.bulk_create(
                list([get_protocol_part(i, part) for i, part in zip(range(1, len(protocol.parts) + 1), protocol.parts)])
            )
        committee_meeting.protocol_parts_update_date = datetime.now()
        committee_meeting.save()

def reparse_protocol(committee_meeting, redownload=True, mks=None, mk_names=None):
    if redownload: redownload_protocol(committee_meeting)
    if committee_meeting.committee.type == 'plenum':
        parse_for_existing_meeting(committee_meeting)
    else:
        create_protocol_parts(committee_meeting, delete_existing=True)
        find_attending_members(committee_meeting, mks, mk_names)


def find_attending_members(committee_meeting, mks=None, mk_names=None):
    logger.debug('find_attending_members')
    if mks is None and mk_names is None:
        logger.debug('get_all_mk_names')
        mks, mk_names = get_all_mk_names()
    with CommitteeMeetingProtocol.get_from_text(
            committee_meeting.protocol_text) as protocol:
        attended_mk_names = protocol.find_attending_members(mk_names)
        for name in attended_mk_names:
            i = mk_names.index(name)
            if not party_at(mks[i], committee_meeting.date):  # not a member at time of this meeting?
                continue  # then don't search for this MK.
            committee_meeting.mks_attended.add(mks[i])
    logger.debug('meeting %d now has %d attending members' % (
        committee_meeting.id,
        committee_meeting.mks_attended.count()))


def Parse(reparse, logger, meeting_pks=None):
    logger.debug('Parse (reparse=%s, meeting_pks=%s)'%(reparse, meeting_pks))
    if meeting_pks is not None:
        meetings = CommitteeMeeting.objects.filter(pk__in=meeting_pks)
    else:
        plenum=Committee.objects.filter(type='plenum')[0]
        meetings=CommitteeMeeting.objects.filter(committee=plenum).exclude(protocol_text='')
    (mks,mk_names)=get_all_mk_names()
    logger.debug('got mk names: %s, %s'%(mks, mk_names))
    for meeting in meetings:
        if reparse or meeting.parts.count() == 0:
            logger.debug('creating protocol parts for meeting %s'%(meeting,))
            meeting.create_protocol_parts(delete_existing=reparse,mks=mks,mk_names=mk_names)


def parse_for_existing_meeting(meeting):
    Parse(True, logger, [meeting.pk])


def _copy(url, to, recopy=False):
    # logger.debug("copying from "+url+" to "+to)
    d = os.path.dirname(to)
    if not os.path.exists(d):
        os.makedirs(d)
    if not os.path.exists(to) or recopy:
        urllib.urlretrieve(url, to + ".tmp")
        os.rename(to + '.tmp', to)
    else:
        logger.debug(u'already downloaded url %s' % url)


def _doc_to_xml(filename):
    cmd = 'antiword -x db ' + filename + ' > ' + filename + '.awdb.xml'
    logger.debug('Generated antiword command %s' % cmd)
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    logger.debug('Antiword output: %s' % output)
    with open(filename + '.awdb.xml', 'r') as f:
        xmldata = f.read()

    logger.debug('len(xmldata) = ' + str(len(xmldata)))
    os.remove(filename + '.awdb.xml')
    return xmldata


def _antiword(filename):
    try:
        return _doc_to_xml(filename)
    except:
        logger.exception(u'antiword failure with file: %s' % filename)
        return ''


def download_for_existing_meeting(meeting):
    DATA_ROOT = getattr(settings, 'DATA_ROOT')
    _copy(meeting.src_url, DATA_ROOT + 'plenum_protocols/tmp')
    xmlData = _antiword(DATA_ROOT + 'plenum_protocols/tmp')
    os.remove(DATA_ROOT + 'plenum_protocols/tmp')
    meeting.protocol_text = xmlData
    meeting.save()
