# coding=utf8
from django.core.management.base import BaseCommand

import datetime
import logging
import smpplib.gsm
import smpplib.client
import smpplib.consts

h1 = datetime.timedelta(hours=1)

from django.conf import settings

def mkGetPdu(op: str):
    def getPdu(pdu):
        try:
            source = pdu.parsed['saddress']
            target = pdu.parsed['daddress']
            message = pdu.parsed.get('sm', '') + pdu.parsed.get('payload', '')
            from sms import models
            if 'submit date:' not in message:
                sms = models.SMS(direction=1, sphone=source, tphone=target, message=message, sended=True, op=op)
                sms.message = "".join(filter(lambda x: x not in ['\u0000'], sms.message))
                sms.save()

        except Exception as e:
           logging.error(e)

    return getPdu


def mkGenMessages(op, num):
    def GenMessages():
        from sms.models import SMS
        newSMS = list(SMS.objects.filter(op=op, direction=0, sended=False)[:100])

        if newSMS:
            for sms in newSMS:
                if not sms.sphone:
                    sms.sphone = num
                sms.sended = True
                sms.save()
                yield (sms.sphone, sms.tphone, sms.message)
        yield None

    return GenMessages


class Command(BaseCommand):
    help = 'serve SMPP requests'

    def add_arguments(self, parser):
        parser.add_argument('op', help='tele2/mts/beeline')

    def handle(self, *args, **options):
        logging.basicConfig(level='DEBUG')
        try:
            op = options['op']
            s = settings.SMPP[op]
        except:
            logging.error("no such config")
            exit()

        timeout = 15
        if options['op'] == 'megafon':
            timeout = 60
        client = smpplib.client.Client(s['ip'], s['port'], timeout)

        client.set_message_received_handler(mkGetPdu(op))
        client.set_message_source(mkGenMessages(op, s['source']))
        client.connect()

        client.bind_transceiver(system_id=s['system_id'], password=s['password'])
        try:
            client.listen([11])
        except Exception as e:
            logging.error(e)
