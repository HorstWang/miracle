from optparse import OptionParser
import xml.etree.ElementTree as ET

import inspect, sys, os, django

sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kattegat.settings")
django.setup()

from vplex.models import event_code
from django.db import connection

def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-v", "--version", dest="version",
                      help="specify VPlex version", metavar="VERSION")

    (options, args) = parser.parse_args()

    if options.filename is None:
        raise RuntimeError('Must specify an error code xml!')
    if options.version is None:
        raise RuntimeError('Must specify a VPlex version!')

    with connection.cursor() as cursor:
        cursor.execute('select count(*) as cnt from vplex_event_code where version = \'%s\'' % options.version)
        existing_count = cursor.fetchall()[0][0]
        if existing_count != 0:
            print('There is existing event code stored for version %s, will not import...' % options.version)
            return
        else:
            print('There is no existing event code stored for version %s, start to import now...' % options.version)
        
    version = options.version

    tree = ET.parse(options.filename)
    root = tree.getroot()

    event_code_rows = []
    for event in root.findall('event'):
        component = 'N/A'
        eventCode = 'N/A'
        internalRCA = 'N/A'
        customerRCA = 'N/A'
        customerDescription = 'N/A'
        formatString = 'N/A'
        component = event.find('component').text
        eventCode = event.find('eventCode').text
        eventRCAandRemedy = event.find('eventRCAandRemedy')
        internalRCA = eventRCAandRemedy.find('internalRCA').text
        customerRCA = eventRCAandRemedy.find('customerRCA').text
        details = event.find('details')
        customerDescription = details.find('customerDescription').text
        formatString = details.find('formatString').text
        #print('component - %s\neventCode - %s\ninternalRCA - %s\ncustomerRCA - %s\ncustomerDescription - %s\nformatString - %s' % (component, eventCode, internalRCA, customerRCA, customerDescription, formatString))
        event_code.objects.create(version = version or 'N/A', component = component or 'N/A', code = eventCode or -1, internalRCA = internalRCA or 'N/A', customerRCA = customerRCA or 'N/A', customerDescription = customerDescription or 'N/A', formatString = formatString or 'N/A')

    with connection.cursor() as cursor:
        sql = 'UPDATE vplex_event_code SET component = \'splitter\' WHERE component = \'spltr\''
        cursor.execute(sql)

    print('Importing process completed...')

if __name__ == '__main__':
    main()