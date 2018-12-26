import sys
from datetime import datetime
import traceback
import os
from os import path
import re
import socket
import shutil
import pandas as pd
import traceback
from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import *
from .utils import CDLogDownloader, LocalFolderUtil, SQLUtil, cached_pd, SafeConvertUtil, log_extract_jobstate
from .models import Investigation, CDLog, cluster, director, CDLog_Extraction_Job
from .loghandler.cdloghandler import CDLogHandler
from .filters import *

import json

local_cdlog_store = '/log_download'

def json_response(hash_object):
    json_str = json.JSONEncoder().encode(hash_object)
#   print(json_str)
    return HttpResponse(json_str, content_type='application/json')
    pass

def get_params(request):
    return getattr(request, request.method)
    pass

# Create your views here.
def index(request):
    return render(request, 'index.html')
    pass

def base_template(request):
    return render(request, 'base.html')
    pass
    
''''''''''''''''''''''''''''''
'''      Grab Data         '''
''''''''''''''''''''''''''''''
def existing_investigations(request):
    investigations = Investigation.objects.all()
    investigation_id_cdlog_id_hash = {}
    for investigation in investigations:
        print('%s %s %s %s %s' % (investigation.id, investigation.sr_id, investigation.sr_oracle_id, investigation.owner, investigation.description))
        investigation_id_cdlog_id_hash[investigation.id] = []
        for cdlog in CDLog.objects.filter(investigation_id=investigation.id):
            print(' %s cdlog id' % cdlog.id)
            investigation_id_cdlog_id_hash[investigation.id].append(cdlog.id)
    print(investigation_id_cdlog_id_hash)
    return render(request, 'existing_investigations.html', { 'page_header': 'Investigations', 'investigations': investigations, 'investigation_id_cdlog_id_hash': investigation_id_cdlog_id_hash })
    pass

def new_investigation(request):
    if request.method == 'GET':
        new_investigation_form = create_investigation_form()
        attach_log_form = cd_log_attach_form()
        return render(request, 'new_investigation.html', { 'page_header': 'New investigation', 'new_investigation_form': new_investigation_form, 'attach_log_form': attach_log_form })
    if request.method == 'POST':
        chunk_trim_regex = re.compile('^.*?(\'|\")(.*?)(\'|\")$')
        params = get_params(request)
        investigation = Investigation.objects.create(sr_id=params['sr_id'], sr_oracle_id=params['oracle_sr_id'], owner=params['owner'], description=params['description'])
        cdlog_ids = []
        cdlog_ids_params = ''
        cdlog_file_stream = request.FILES["cdlog_file"]
        cdlog_file_name = str(cdlog_file_stream)
        print(cdlog_file_name)
        with open('/log_download/%s' % cdlog_file_name, 'wb+') as destination:
            for chunk in cdlog_file_stream.chunks():
                destination.write(chunk)
        cdlog = CDLog.objects.create(investigation_id=investigation.id, serial_number=cdlog_file_name.split('-')[0], remote_directory=path.join(local_cdlog_store, cdlog_file_name), local_directory=path.join(local_cdlog_store, cdlog_file_name.replace('.tar.gz', '')))
        extraction_job = CDLog_Extraction_Job.objects.create(cdlog_id=cdlog.id, cdlog_file=path.join(local_cdlog_store, cdlog_file_name), extracted_folder=path.join(local_cdlog_store, cdlog_file_name.replace('.tar.gz', '')), state=log_extract_jobstate.NOT_STARTED)
#       for remote_path in params['remote_log_path'].split('\r\n'):
#           cdlog = CDLog.objects.create(investigation_id=investigation.id, serial_number=remote_path.split('/')[-1].split('-')[0], remote_directory=remote_path, local_directory=local_cdlog_store)
#           cdlog_ids.append(cdlog.id)
#           cdlog_ids_params = cdlog_ids_params + 'cdlog_id=%s' % cdlog.id + '&'
#           print('%s to %s...' % (remote_path, local_cdlog_store))
#       new_investigation_form = create_investigation_form(initial={ 'sr_id': params['sr_id'], 'oracle_sr_id': params['oracle_sr_id'], 'owner': params['owner'], 'description': params['description']})
#       attach_log_form = cd_log_attach_form(initial={ 'remote_log_path': params['remote_log_path'] })
        #return render(request, 'new_investigation.html', { 'page_header': 'New investigation', 'new_investigation_form': new_investigation_form, 'attach_log_form': attach_log_form })
        return HttpResponseRedirect('monitor_cdlog_extraction?extraction_job_id=%s' % extraction_job.id)
    pass

def monitor_cdlog_extraction(request):
    params = get_params(request)
    extraction_job_id = params['extraction_job_id']
    return render(request, 'monitor_cdlog_extraction.html', { 'page_header': 'CDLog extraction job state monitor', 'extraction_job_id': extraction_job_id })

def dump_cdlog_to_database(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    return render(request, 'dump_cdlog_to_database.html', { 'page_header': 'Dump CDLOG to database', 'cdlog_id': cdlog_id })

def api_monitor_dump_cdlog_to_database(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    return raw_execute('select id, investigation_id, hardware_type, local_directory, remote_directory, dump_started, dump_succeeded, dump_completed, code_level, product_type, serial_number from vplex_cdlog where id = %s' % cdlog_id)
    
def api_dump_cdlog_to_database(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    cdlog = CDLog.objects.get(pk=cdlog_id)
    hash_result = {}
    
    if not cdlog.dump_started:
        try:
            cdlog.dump_started = True
            cdlog.save()
            hash_result['dump_started'] = True
            
            print('====================Start to parse===================')
            cdloghandler = CDLogHandler(cdlog.id)
            print('*******************************')
            cdloghandler.parse()
            print('====================Finish parsing===================')
            
            cdlog.dump_succeeded = True
            cdlog.save()
            hash_result['dump_succeeded'] = True
            pass
        except:
            (exc_info, exc_value, exc_stacktrace) = sys.exc_info()
            cdlog.dump_succeeded = False
            hash_result['dump_succeeded'] = False
            cdlog.exception = str(exc_info)
            hash_result['exception'] = str(exc_info)
            cdlog.save()
            
            print(exc_info)
            print(exc_value)
            traceback.print_tb(exc_stacktrace)
        finally:
            hash_result['dump_completed'] = True
            cdlog.dump_completed = True
            cdlog.save()

    return raw_execute('select id, investigation_id, hardware_type, local_directory, remote_directory, dump_started, dump_succeeded, dump_completed, code_level, product_type, serial_number from vplex_cdlog where id = %s' % cdlog_id)

def batch_cdlog_load(request):
    params = get_params(request)
    cdlog_id_lst = params.getlist('cdlog_id')
    cdlog_lst = []
    for cdlog_id in cdlog_id_lst:
        cdlog_lst.append(CDLog.objects.get(pk=cdlog_id))
    return render(request, 'batch_cdlog_load.html', { 'cdlog_id_lst': cdlog_id_lst, 'cdlog_lst': cdlog_lst })
    pass

def load_from_log_server(request):
    hash_result = { 'download_started': False, 'download_succeeded': False, 'dump_started': False, 'dump_succeeded': False, 'exception': None }
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    force = 'force' in params
    if force:
        print('*****************************************************************************************************************************************************************************************************')
    else:
        print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    cdlog = CDLog.objects.get(pk=cdlog_id)
    remote_directory = cdlog.remote_directory
    local_directory = cdlog.local_directory
    downloaded_to = path.join(local_directory, path.basename(remote_directory))
    cdlog.save()
    print('%s to %s' % (cdlog.local_directory, cdlog.remote_directory))
    
    if force:
        cdlog.download_started = False
        cdlog.download_completed = False
        cdlog.download_succeeded = False
        cdlog.dump_started = False
        cdlog.dump_succeeded = False
        cdlog.dump_completed = False
        print('Deleting %s' % downloaded_to)
        shutil.rmtree(downloaded_to)
    
    print('==============Downloaded started %s================' % cdlog.download_started)
    if not cdlog.download_started:
        try:
            cd_log_downloader = CDLogDownloader('10.241.171.130', 'vplexuser', 'vplexuser')
            hash_result['downloaded_to'] = downloaded_to
            hash_result['download_started'] = True
            cdlog.download_started = True
            cdlog.save()
            if not path.exists(path.join(local_directory, path.basename(remote_directory))):
                cd_log_downloader.thin_download(remote_directory, local_directory)
            else:
                print('-----------------Folder exists, skipping download steps-----------------')
            hash_result['download_succeeded'] = True
            cdlog.download_succeeded = True
            cdlog.save()
        except:
            (exc_info, exc_value, exc_stacktrace) = sys.exc_info()
            print('------Exception infor start------')
            print(exc_info)
            print(exc_value)
            traceback.print_tb(exc_stacktrace)
            print('------Exception infor ended------')
            cdlog.download_succeeded = False
            hash_result['download_succeeded'] = False
            cdlog.exception = str(exc_info)
            hash_result['exception'] = str(exc_info)
            cdlog.save()          
        finally:
            cdlog.download_completed = True
            cdlog.save()

    print('==============Dump started %s================' % cdlog.dump_started)
    print('==============Download succeeded %s================' % cdlog.download_succeeded)
    if not cdlog.dump_started and cdlog.download_succeeded:
        try:
            cdlog.dump_started = True
            cdlog.save()
            hash_result['dump_started'] = True
            
            print('====================Start to parse===================')
            cdloghandler = CDLogHandler(cdlog.id)
            print('*******************************')
            cdloghandler.parse()
            print('====================Finish parsing===================')
            
            cdlog.dump_succeeded = True
            cdlog.save()
            hash_result['dump_succeeded'] = True
            pass
        except:
            (exc_info, exc_value, exc_stacktrace) = sys.exc_info()
            cdlog.dump_succeeded = False
            hash_result['dump_succeeded'] = False
            cdlog.exception = str(exc_info)
            hash_result['exception'] = str(exc_info)
            cdlog.save()
            
            print(exc_info)
            print(exc_value)
            traceback.print_tb(exc_stacktrace)
        finally:
            hash_result['dump_completed'] = True
            cdlog.dump_completed = True
            cdlog.save()
        
    return json_response([hash_result])
    pass

def view_cdlog_load_state(request):
    result = []
    
    params = get_params(request)
    cdlog_id_lst = params.getlist('cdlog_id')
    for cdlog_id in cdlog_id_lst:
        print('-------Searching cdlog_id %s-------' % cdlog_id)
        cdlog = CDLog.objects.get(pk=cdlog_id)
        downloaded_to = path.join(cdlog.local_directory, path.basename(cdlog.remote_directory))
        downloaded_size = LocalFolderUtil.get_folder_size(downloaded_to)
        print('%s - %s' % (downloaded_to, downloaded_size))
        
        cdlog_hash = {}
        cdlog_hash["id"] = cdlog_id
        cdlog_hash["remote_directory"] = cdlog.remote_directory
        cdlog_hash["local_directory"] = cdlog.local_directory
        cdlog_hash["download_started"] = cdlog.download_started
        cdlog_hash["download_completed"] = cdlog.download_completed
        cdlog_hash["download_succeeded"] = cdlog.download_succeeded
        cdlog_hash["downloaded_size"] = downloaded_size
        cdlog_hash["dump_started"] = cdlog.dump_started
        cdlog_hash["dump_completed"] = cdlog.dump_completed
        cdlog_hash["dump_succeeded"] = cdlog.dump_succeeded
        cdlog_hash["exception"] = cdlog.exception
        result.append(cdlog_hash)
        
    return json_response(result)
    pass

def cdlog_analysis_home(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    cluster_hierachy = {}
    cluster_sql = 'select c.name as cluster, c.serial_number as cluster_serial_number, ' \
        'd.name as director, ' \
        'p.name as port, p.address as port_address, p.role as port_role, p.status as port_status, ' \
        's.manufacturer as sfps_manufacturer, s.part_number as sfps_part_number, s.serial_number as sfps_serial_number, ' \
        's.rx_power as sfps_rx_power, s.tx_power as sfps_tx_power, s.temprature as sfps_temprature, ' \
        'c.id as cluster_id, d.id as director_id, p.id as port_id, s.id as sfps_id ' \
        'from vplex_cluster as c ' \
        'join vplex_director as d on d.cluster_id = c.id ' \
        'join vplex_port as p on p.director_id = d.id ' \
        'left join vplex_sfps as s on s.port_id = p.id where c.cdlog_id = %s' % cdlog_id
    view_initiator_sql = 'select v.id as view_id, v.name, i.name as initiator, ' \
                    'i.wwnn, i.wwpn, i.host_type, i.logged_in, i.cross_connected as view_name '\
                    ' from vplex_storage_view as v join vplex_view_initiator as i on i.view_id = v.id where v.cluster_id in (select id from vplex_cluster where cdlog_id = %s)' % cdlog_id
    view_port_sql = 'select v.id as view_id, v.name as view_name, ' \
            'd.name as director, ' \
            'p.name as port_name, p.address as port_address, p.role as port_role, p.status as port_status ' \
            ' from vplex_storage_view as v join vplex_view_port as vp on vp.view_id = v.id join vplex_port as p on vp.port_id = p.id join vplex_director as d on d.id = p.director_id where v.cluster_id in (select id from vplex_cluster where cdlog_id = %s)' % cdlog_id
    print(cluster_sql)
    with connection.cursor() as cursor:
        cursor.execute(cluster_sql)
        for row in cursor.fetchall():
            clstr = str(row[0])
            clstr_serial_number = str(row[1])
            director = str(row[2])
            engine = 'engine-%s' % director[9:12]
            port = str(row[3])
            port_address = str(row[4])
            port_role = str(row[5])
            port_status = str(row[6])
            sfps_manufacturer = str(row[7])
            sfps_part_number = str(row[8])
            sfps_serial_number = str(row[9])
            sfps_rx_power = str(row[10])
            sfps_tx_power = str(row[11])
            sfps_temprature = str(row[12])
            cluster_id = str(row[13])
            director_id = str(row[14])
            port_id = str(row[15])
            sfps_id = str(row[16])
            print('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s' % row)
            if not clstr in cluster_hierachy:
                cluster_hierachy[clstr] = {}
            if not 'serial_number' in cluster_hierachy[clstr]:
                cluster_hierachy[clstr]['serial_number'] = clstr_serial_number
            if not 'engines' in cluster_hierachy[clstr]:
                cluster_hierachy[clstr]['id'] = cluster_id
                cluster_hierachy[clstr]['engines'] = {}
            if not engine in cluster_hierachy[clstr]['engines']:
                cluster_hierachy[clstr]['engines'][engine] = {}
            if not 'directors' in cluster_hierachy[clstr]['engines'][engine]:
                cluster_hierachy[clstr]['engines'][engine]['directors'] = {}
            if not director in cluster_hierachy[clstr]['engines'][engine]['directors']:
                cluster_hierachy[clstr]['engines'][engine]['directors'][director] = { 'id': director_id }
            if not 'ports' in cluster_hierachy[clstr]['engines'][engine]['directors'][director]:
                cluster_hierachy[clstr]['engines'][engine]['directors'][director]['director_side'] = director[-1].lower()
                cluster_hierachy[clstr]['engines'][engine]['directors'][director]['ports'] = {}
            if not port in cluster_hierachy[clstr]['engines'][engine]['directors'][director]['ports']:
                cluster_hierachy[clstr]['engines'][engine]['directors'][director]['ports'][port] = { 'id': port_id, 'address': port_address, 'role': port_role, 'status': port_status, 'manufacturer': sfps_manufacturer, 'part_number': sfps_part_number, 'serial_number': sfps_serial_number, 'rx_power': sfps_rx_power, 'tx_power': sfps_tx_power, 'temprature': sfps_temprature }
                
        cursor.execute(view_initiator_sql)
        for row in cursor.fetchall():
            print(row)

    print('Cluster hierachy : ')
    print(cluster_hierachy)
    
    for clst in cluster_hierachy.keys():
        print(clst)
        
    search_form = search_component_form(initial={ 'cdlog_id': cdlog_id })
    date_span_picker = date_span_picker_form(initial={ 'start_date_time': datetime.now(), 'end_date_time': datetime.now() })
    print('cluster size : %s' % len(cluster_hierachy.keys()))
    return render(request, 'cdlog_analysis_home.html', { 'page_header': 'Analyze VPlex cdlog', 'cluster_hierachy': cluster_hierachy, 'site_size': len(cluster_hierachy.keys()), 'cluster_panel_size': int(12/len(cluster_hierachy.keys())), 'cdlog_id': cdlog_id, 'search_form': search_form, 'date_span_picker_form': date_span_picker })
    pass
    
def initiator_report(request):
    return render(request, 'initiator_report.html', { 'page_header': 'Initiator report' })
    pass
   
def sql_run(sql):
    result = { 'description': None, 'rows': [] }

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result['description'] = [i[0] for i in cursor.description]
        result['rows'] = cursor.fetchall()
    return result
   
def raw_execute(sql):
    result = { 'description': None, 'rows': [] }
    
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result['description'] = [i[0] for i in cursor.description]
        result['rows'] = cursor.fetchall()
        
    return json_response(result)
    pass

def raw_desc_table(request):
    params = get_params(request)
    table = params['table']
    sql = 'desc %s' % table
    return raw_execute(sql)
    pass

def desc_table(request):
    params = get_params(request)
    table = params['table']
    sql = 'desc %s' % table
    result = sql_run(sql)
    print(result)
    columns = [row[0] for row in result['rows']]
    return json_response(columns)
    pass

def raw_execute_group_by(request):
    params = get_params(request)
    group_columns = params.getlist('group_column')
    table = params['table']
    group_columns_str = ', '.join(group_columns)
    where_list = params.getlist('where')
    for where in where_list:
        print(where)
    where_statement = ''
    if not where_list is None and len(where_list) > 0:
        where_statement = ' where ' + ' and '.join(where_list)
    sql = 'select %s, count(*) as cnt from %s %s group by %s' % (group_columns_str, table, where_statement, group_columns_str)
    return raw_execute(sql)
    pass
    
def api_event_code(request):
    params = get_params(request)
    rob_get_param = lambda p, key: p[key] if key in p else None
    cdlog_id = rob_get_param(params, 'cdlog_id')
    sql = 'select * from vplex_event_code'
        
    return raw_execute(sql)
    pass
    
def api_cluster_director_port(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select distinct c.id as cluster_id, c.name as cluster, ' \
        'd.id as director_id, d.name as director, ' \
        'p.id as port_id, p.name as port, p.address as port_address, p.role as port_role, p.status as port_status ' \
        'from vplex_port as p ' \
        'join vplex_director as d on p.director_id = d.id ' \
        'join vplex_cluster as c on d.cluster_id = c.id ' \
        'where c.cdlog_id = %s' % cdlog_id
        
    return raw_execute(sql)
    pass
    
def api_cluster_storage_view(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select c.id as cluster_id, c.name as cluster, ' \
        'v.id as storage_view_id, v.name as storage_view ' \
        'from vplex_cluster as c ' \
        'join vplex_storage_view as v on v.cluster_id = c.id where c.cdlog_id = %s' % cdlog_id
        
    return raw_execute(sql)
    pass
    
def api_cluster_storage_view_initiator_target_login(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select i.id as initiator_id, i.name as initiator, i.wwnn as initiator_wwnn, i.wwpn as initiator_wwpn, ' \
        'v.id as storage_view_id, v.name as storage_view_name, v.status as storage_view_status, ' \
        'p.id as port_id, p.name as port, p.address as port_address, p.status as port_status, ' \
        'd.id as director_id, d.name as director, d.ip as director_ip, d.uid as director_uid, ' \
        'c.id as cluster_id, c.name as cluster, c.serial_number as cluster_serial_number ' \
        'from vplex_view_initiator as i ' \
        'left join vplex_view_initiator_target_login as l on l.view_initiator_id = i.id ' \
        'left join vplex_view_port as vp on l.view_port_id = vp.id ' \
        'left join vplex_port as p on vp.port_id = p.id ' \
        'join vplex_storage_view as v on i.view_id = v.id ' \
        'left join vplex_director as d on p.director_id = d.id ' \
        'left join vplex_cluster as c on v.cluster_id = c.id where c.cdlog_id = %s' % cdlog_id
        #'from vplex_view_initiator_target_login as l ' \
        #'join vplex_view_initiator as i on l.view_initiator_id = i.id ' \
        
    return raw_execute(sql)
    pass
    
def api_cluster_storage_view_initiator(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select c.id as cluster_id, c.name as cluster, ' \
        'v.id as storage_view_id, v.name as storage_view, ' \
        'i.id as initiator_id, i.name as initiator, i.wwnn, i.wwpn, i.host_type, i.logged_in, i.cross_connected ' \
        'from vplex_cluster as c ' \
        'join vplex_storage_view as v on v.cluster_id = c.id ' \
        'join vplex_view_initiator as i on i.view_id = v.id where c.cdlog_id = %s' % cdlog_id
        
    return raw_execute(sql)
    pass
    
def api_cluster_engine_director(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select distinct c.id as cluster_id, c.name as cluster, ' \
        'concat(\'engine\', substr(d.name, 9, 4)) as engine, ' \
        'd.id as director_id, d.name as director, ' \
        'p.id as port_id, p.name as port, p.address as port_address ' \
        'from vplex_cluster as c ' \
        'join vplex_director as d on d.cluster_id = c.id ' \
        'join vplex_port as p on p.director_id = d.id ' \
        'join vplex_storage_array_connectivity as ac on ac.i = p.address ' \
        'join vplex_storage_array as a on ac.storage_array_id = a.id and a.cdlog_id = c.cdlog_id where c.cdlog_id = %s' % cdlog_id
        
    return raw_execute(sql)
    pass
    
def api_cluster_array(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select distinct c.id as cluster_id, c.name as cluster, c.serial_number, ' \
        'a.id as array_id, a.name as array, ' \
        'a.vendor, a.revision ' \
        'from vplex_cluster as c ' \
        'join vplex_director as d on d.cluster_id = c.id ' \
        'join vplex_port as p on p.director_id = d.id ' \
        'join vplex_storage_array_connectivity as ac on ac.i = p.address ' \
        'join vplex_storage_array as a on ac.storage_array_id = a.id and a.cdlog_id = c.cdlog_id where c.cdlog_id = %s' % cdlog_id
        
    return raw_execute(sql)
    pass

def api_cluster_array_target(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select distinct c.id as cluster_id, c.name as cluster, c.serial_number, ' \
        'a.id as array_id, a.name as array, ' \
        'ac.t as target, ' \
        'a.vendor, a.revision ' \
        'from vplex_cluster as c ' \
        'join vplex_director as d on d.cluster_id = c.id ' \
        'join vplex_port as p on p.director_id = d.id ' \
        'join vplex_storage_array_connectivity as ac on ac.i = p.address ' \
        'join vplex_storage_array as a on ac.storage_array_id = a.id and a.cdlog_id = c.cdlog_id ' \
        'where c.cdlog_id = %s' % cdlog_id
        
    return raw_execute(sql)
    pass
    
def api_cluster_array_connectivity(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select c.id as cluster_id, c.name as cluster, c.serial_number, ' \
        'd.id as director_id, d.name as director, ' \
        'p.id as port_id, p.name as port, p.address as port_address, ' \
        'ac.t as target, ' \
        'a.id as array_id, a.name as array ' \
        'from vplex_cluster as c ' \
        'join vplex_director as d on d.cluster_id = c.id ' \
        'join vplex_port as p on p.director_id = d.id ' \
        'join vplex_storage_array_connectivity as ac on ac.i = p.address ' \
        'join vplex_storage_array as a on ac.storage_array_id = a.id and a.cdlog_id = c.cdlog_id where c.cdlog_id = %s' % cdlog_id

    return raw_execute(sql)
    pass
    
def api_sys_perf_log_available_director(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select distinct c.id as cluster_id, c.name as cluster_name, ' \
            'd.id as director_id, d.name as director_name ' \
            'from vplex_director as d ' \
            'join vplex_cluster as c on d.cluster_id = c.id ' \
            'join vplex_sysperflog as spl on spl.director_id = d.id where c.cdlog_id = %s' % cdlog_id

    return raw_execute(sql)
    pass
    
def api_sys_perf_log(request):
    params = get_params(request)
    cdlog_id = params['cdlog_id']
    sql = 'select distinct c.id as cluster_id, c.name as cluster_name, ' \
            'd.id as director_id, d.name as director_name, ' \
            'spl.id as sysperlog_id, spl.path as sysperflog ' \
            'from vplex_director as d ' \
            'join vplex_cluster as c on d.cluster_id = c.id ' \
            'join vplex_sysperflog as spl on spl.director_id = d.id where c.cdlog_id = %s' % cdlog_id

    return raw_execute(sql)
    pass
    
def api_sys_perf_log_columns(request):
    params = get_params(request)
    director_id = params['director_id']
    sql = 'select spl.path as sysperflog from vplex_director as d join vplex_cluster as c on d.cluster_id = c.id join vplex_sysperflog as spl on spl.director_id = d.id where spl.director_id = %s limit 1' % director_id
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        if len(rows) == 0:
            return json_response({})
        else:
            log_path = rows[0][0]
            df = cached_pd.read_csv(log_path)
            headers = list(df.columns)
            return json_response(headers)
    pass

def api_vv_perf_log_columns(request):
    params = get_params(request)
    director_id = params['director_id']
    log = help_vv_perf_path_for_director(director_id)[0]
    df = cached_pd.read_csv(log)
    columns = list(df.columns)
    return json_response(columns)
    
def help_sys_perf_path_for_director(director_id):
    logs = []
    for row in SQLUtil.execute_sql_rows('select path from vplex_sysperflog where director_id = %s' % director_id):
        logs.append(row[0])
    return logs

def help_vv_perf_path_for_director(director_id):
    logs = []
    for row in SQLUtil.execute_sql_rows('select path from vplex_vvperflog where director_id = %s' % director_id):
        logs.append(row[0])
    return logs
    
def api_sys_perf_log_timespan(request):
    params = get_params(request)
    director_id = params['director_id']
    df = pd.DataFrame()
    for log in help_sys_perf_path_for_director(director_id):
        df_s = cached_pd.read_csv(log)
        df = pd.concat([df, df_s])
    timestamps = list(df['Time'])
    len_timestamps = len(timestamps)
    start = int(datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S').timestamp())
    end = int(datetime.strptime(timestamps[len_timestamps - 1], '%Y-%m-%d %H:%M:%S').timestamp())
    return json_response([start, end])
    pass
    
def api_sys_perf_log_timestamps(request):
    params = get_params(request)
    director_id = params['director_id']
    df = pd.DataFrame()
    for log in help_sys_perf_path_for_director(director_id):
        df_s = cached_pd.read_csv(log)
        df = pd.concat([df, df_s])
    timestamps = list(df['Time'])
    len_timestamps = len(timestamps)
    for i in range(0, len_timestamps):
        timestamps[i] = int(datetime.strptime(timestamps[i], '%Y-%m-%d %H:%M:%S').timestamp())
    return json_response(timestamps)
    pass

def api_vv_perf_log_available_volumes(request):
    params = get_params(request)
    director_id = params['director_id']
    df = pd.DataFrame()
    logs = help_vv_perf_path_for_director(director_id)
    for log in logs:
        df_s = cached_pd.read_csv(log)
        df = pd.concat([df, df_s])
    volumes = list(df['Virtual Volume'].unique())
    return json_response(volumes)
    pass

def api_sys_perf_log_by_columns(request):
    params = get_params(request)
    columns = params.getlist('column')
    start_date_time = int(params['start_date_time'])
    end_date_time = int(params['end_date_time'])
    perf_type = params['perf_type']
    vv_names = []
    print(params)
    if 'vv_name' in params:
        vv_names = params.getlist('vv_name')
        print(vv_names)
    merge_action = None
    supported_merge_actions = ( 'dir_sum', 'dir_avg' )

    serieses = []
    
    if 'merge_action' in params:
        merge_action = params['merge_action']
        if not merge_action in supported_merge_actions:
            raise RuntimeError('%s is not a supported action, supported actions are %s.' % (merge_action, supported_merge_actions))
    parse_column_re = re.compile('^\s*(\d+)_(.+?)\s*$')
    column_param_dict = {}
    for column in columns:
        parse_column_m = parse_column_re.search(column)
        if parse_column_m is None:
            raise RuntimeError("Failed to parse column parameter : %s" % column)
        director_id = parse_column_m.group(1)
        column_name = parse_column_m.group(2)
        if not director_id in column_param_dict:
            column_param_dict[director_id] = []
        column_param_dict[director_id].append(column_name)

    for director_id, column_names in column_param_dict.items():
        df = pd.DataFrame()
        director_obj = director.objects.get(id=director_id)
        director_name = director_obj.name
        logs = []
        if perf_type == 'sys':
            logs = help_sys_perf_path_for_director(director_id)
        elif perf_type == 'vv':
            logs = help_vv_perf_path_for_director(director_id)
        else:
            raise RuntimeError('Unsupported performance type \'%s\' ...' % perf_type)
        for log in logs:
            df_s = cached_pd.read_csv(log)
            if len(vv_names) > 0:
                df_s = df_s.loc[df_s['Virtual Volume'].isin(vv_names)]
            df = pd.concat([df, df_s])
            df = df.loc[(df['Time (UTC)'].astype('int64') >= start_date_time) & (df['Time (UTC)'].astype('int64') <= end_date_time)]
        timestamps = list(df['Time (UTC)'])
        len_timestamps = len(timestamps)
        len_index = len(df.index)

#       for i in range(0, len_timestamps):
#           timestamps[i] = int(datetime.strptime(timestamps[i], '%Y-%m-%d %H:%M:%S').timestamp()) * 1000
        if merge_action is None:
            for column_name in column_names:
                column_result_rows = []
                column_data = list(df[column_name])
                for i in range(0, len_timestamps):
                    column_result_rows.append([timestamps[i], column_data[i]])
                print('%s %s' % (director_name, column_name))
                serieses.append({ 'name': '%s %s' % (director_name, column_name), 'data': column_result_rows })
        else:
            selected_df = df[column_names]
            len_column_names = len(column_names)
            merged_result_rows = []
            for i in range(0, len_timestamps):
                merged_result_row = [ timestamps[i] ]
                if merge_action in ('dir_sum', 'sum'):
                    merged_result_value = sum([SafeConvertUtil.to_float(v) for v in list(selected_df.iloc[i])])
                elif merge_action in ('dir_avg', 'avg'):
                    merged_result_value = sum([SafeConvertUtil.to_float(v) for v in list(selected_df.iloc[i])]) / len_column_names
                merged_result_row.append(merged_result_value)
                merged_result_rows.append(merged_result_row)
            serieses.append({ 'name': director_name, 'data': merged_result_rows })
            
    if not merge_action is None:
        if merge_action == 'sum':
            sum_all_rows = []
            if len(serieses) != 0:
                for i in range(0, len(serieses[0]['data'])):
                    sum_all_rows.append([serieses[0]['data'][i][0], sum([series['data'][i][1] for series in serieses])])
            serieses = [{ 'name': 'Summary all', 'data': sum_all_rows }]
        elif merge_action == 'avg':
            avg_all_rows = []
            if len(serieses) != 0:
                for i in range(0, len(serieses[0]['data'])):
                    avg_all_rows.append([serieses[0]['data'][i][0], sum([series['data'][i][1] for series in serieses]) / len(serieses)])
            serieses = [{ 'name': 'Average all', 'data': avg_all_rows }]
            pass
                    
    return json_response(serieses)
    pass

def api_cdlog_extraction_job(request):
    params = get_params(request)
    extraction_job_id = None
    where_str = ''
    if 'extraction_job_id' in params:
        extraction_job_id = params['extraction_job_id']
        where_str = ' where id = %s' % extraction_job_id
    return raw_execute("select * from vplex_cdlog_extraction_job%s" % where_str)
    
def api_hostname(request):
	return json_response({ 'hostname': socket.gethostname() })
	
''''''''''''''''''''''''''''''''''''''''''
'''              Debug                 '''
''''''''''''''''''''''''''''''''''''''''''
def purge_log_data(request):
    with connection.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE vplex_vvperflog')
        cursor.execute('TRUNCATE TABLE vplex_sysperflog')
        cursor.execute('TRUNCATE TABLE vplex_cdlog_extraction_job')
        cursor.execute('TRUNCATE TABLE vplex_firmwarelog')
        cursor.execute('TRUNCATE TABLE vplex_firmwarelogentry')
        cursor.execute('TRUNCATE TABLE vplex_firmwarelogeventcode')
        cursor.execute('TRUNCATE TABLE vplex_storage_array_connectivity')
        cursor.execute('TRUNCATE TABLE vplex_storage_array')
        cursor.execute('TRUNCATE TABLE vplex_view_initiator_target_login')
        cursor.execute('TRUNCATE TABLE vplex_view_port')
        cursor.execute('TRUNCATE TABLE vplex_view_initiator')
        cursor.execute('TRUNCATE TABLE vplex_storage_view')
        cursor.execute('TRUNCATE TABLE vplex_sfps')
        cursor.execute('TRUNCATE TABLE vplex_port')
        cursor.execute('TRUNCATE TABLE vplex_director')
        cursor.execute('TRUNCATE TABLE vplex_cluster')
        cursor.execute('TRUNCATE TABLE vplex_cdlog')
        cursor.execute('TRUNCATE TABLE vplex_investigation')
        return HttpResponseRedirect('index')
    pass
