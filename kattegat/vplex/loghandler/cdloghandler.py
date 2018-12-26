import os
from os import path
import re
from django.db import connection
from .loghandler import LogHandler
from .firmwareloghandler import FirmwareLogHandler
from ..models import CDLog, cluster, director, port, sfps, storage_view, view_initiator, view_port, view_initiator_target_login, storage_array, storage_array_connectivity, SysPerfLog, VVPerfLog, tach_sh_login
from ..utils import FileUtil, PerformanceFileUtil, LocalFolderUtil, REUtil

class CDLogHandler(LogHandler):
    def __init__(self, cdlog_id):
        self.cdlog = CDLog.objects.get(id=cdlog_id)
        self.directory = self.cdlog.local_directory
        self.cluster_name_dict = {}
        self.director_name_dict = {}
        print('=====================%s====================' % self.directory)
        
    def walk_files(self, file):
        matches = []
        for (root, dirs, files) in os.walk(self.directory):
            if file in files:
                matches.append(path.join(root, file))
            else:
                file_re = re.compile(file)
                for f in files:
                    if file_re.search(f):
                        matches.append(path.join(root, f))
        return matches
        
    fw_log_cluster_regex = re.compile('mgmt_server\/(.*?)\/clilog')

    def parse_cluster(self):
        cluster_list_started = False
        cluster_list_ended = False
        cluster_list_pre_line_re = re.compile('Cluster TLA:')
        cluster_list_post_line_re = re.compile('Clusters:')
        cluster_serial_number_line_re = re.compile('^\s*(\S+?)\s*:\s*(\S+)\s*$')
        for health_check in self.walk_files('HealthCheck.txt'):
            print('Parsing cluster infor %s' % health_check)
            for line in FileUtil.readlines(health_check):
            #   print(line)
                if not cluster_list_started and not cluster_list_pre_line_re.search(line) is None:
                    cluster_list_started = True
                    continue
                if cluster_list_started and not cluster_list_ended:
                    cluster_serial_number_line_m = cluster_serial_number_line_re.search(line)
                    if not cluster_serial_number_line_m is None:
                        (cluster_name, serial_number) = cluster_serial_number_line_m.groups()
                    #   print('%s - %s' % (cluster_name, serial_number))
                        c = cluster.objects.create(cdlog_id=self.cdlog.id, name=cluster_name, serial_number=serial_number)
                        self.cluster_name_dict[cluster_name] = c
                if cluster_list_started and not cluster_list_post_line_re.search(line) is None:
                    cluster_list_ended = True
                    break
    
    def parse_director(self):
        current_cluster_name_re = re.compile('^\s*Cluster\s+(\S+)\s+contains\s+directors?')
        director_re = re.compile('^\s*(director-\d-\d-\w)\s+(\S+)\s+(\S+)\s*$')
        current_cluster_name = None
        cdlog_id = self.cdlog.id
        for directorinfo in self.walk_files('Cluster.txt'):
            print('Parsing director infor from %s' % directorinfo)
            for line in FileUtil.readlines(directorinfo):
                #print(line)
                current_cluster_name_m = current_cluster_name_re.search(line)
                if not current_cluster_name_m is None:
                    current_cluster_name = current_cluster_name_m.group(1)
                    current_cluster = cluster.objects.get(cdlog_id=self.cdlog.id, name=current_cluster_name)
                    current_cluster_id = current_cluster.id
                    #print('Current cluster name : %s Current cluster id : %s' % (current_cluster_name, current_cluster_id))
                if not current_cluster_name is None:
                    director_m = director_re.search(line)
                    if not director_m is None:
                        (director_name, director_ip, director_uuid) = director_m.groups()
                    #   print('%s - %s - %s' % (director_name, director_ip, director_uuid))
                        d = director.objects.create(cluster_id=current_cluster_id, name=director_name, ip=director_ip, uid=director_uuid)
                        self.director_name_dict[director_name] = d
    
    def parse_ports(self):
        director_name_re = re.compile('^\s*Director\s+(director-\d-\d-\w)\s*$')
        port_info_re = re.compile('^\s*(\w\d-\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$')
        sfps_info_re = re.compile('^\s*(\w\d-\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$')
        clsts_ids = [cls.id for cls in cluster.objects.filter(cdlog_id=self.cdlog.id)]
        drcts = director.objects.filter(cluster_id__in=clsts_ids)
        drct_dict = {}
        for drct in drcts:
            drct_dict[drct.name] = drct
        #print(drct_dict)
        for portinfo in self.walk_files('Ports.txt'):
            print('Parsing port & sfps infor %s' % portinfo)
            current_director_name = None
            current_director_port_dict = {}
            for line in FileUtil.readlines(portinfo):
                #print(line)
                director_name_m = director_name_re.search(line)
                if not director_name_m is None:
                    current_director_name = director_name_m.group(1)
                    current_director_port_dict = {}
                if not current_director_name is None:
                    port_info_m = port_info_re.search(line)
                    if not port_info_m is None:
                        (port_name, address, role, status) = port_info_m.groups()
                        if current_director_name in drct_dict:
                            current_director_port_dict[port_name] = port.objects.create(director_id=drct_dict[current_director_name].id, name=port_name, address=address, role=role, status=status)
                    else:
                        sfps_info_m = sfps_info_re.search(line)
                        if not sfps_info_m is None:
                            (port_name, manufacturer, part_number, serial_number, rxpower, txpower, temprature) = sfps_info_m.groups()
                            if port_name in current_director_port_dict:
                                sfps.objects.create(port_id=current_director_port_dict[port_name].id, name=port_name, manufacturer=manufacturer, part_number=part_number, serial_number=serial_number, rx_power=rxpower, tx_power=txpower, temprature=temprature)
    
    def parse_storage_view(self):
        cluster_name_re = re.compile('Cluster\s+Name\s*:\s*(\S+)')
        view_name_re = re.compile('^\s*View\s+Name\s*:\s*(\S+)\s*$')
        view_status_re = re.compile('^\s*View\s+Status\s*:\s*(\S+)\s*$')
        view_initiator_title_re = re.compile('^\s*View\s+Initiator')
        view_initiator_re = re.compile('^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$')
        view_initiator_to_target_title_re = re.compile('initiator\s+to\s+target')
        view_initiator_to_target_re = re.compile('^\s*(\S+)\s+(\S.*?)\s*$')
        view_ports_title_re = re.compile('^\s*View\s+Ports\s*:\s*$')
        view_port_re = re.compile('(\S+?)\s*(\(\s*\d-\d-\w\/\w\d-\S+\s*\))')
        empty_line_re = re.compile('^\s*$')
        parsing_initiator = False
        parsing_initiator_to_target = False
        parsing_port = False
        current_cluster = None
        current_cluster_id = None
        current_cluster_directors = None
        current_cluster_directors_ids = None
        current_cluster_name = None
        current_view_name = None
        current_view_status = None
        current_storage_view = None
        current_storage_view_id = None
        view_mapping_dict = {}
        '''
        view_mapping_dict[$cluster_id][$view_id]['mapping'] { $initiator_name: [$port_identities] }
        view_mapping_dict[$cluster_id][$view_id]['initiator_id'] { $initiator_name : $initiator_id }
        view_mapping_dict[$cluster_id][$view_id]['port_id'] { $port_identity : $port_id }
        '''
        for view in self.walk_files('Host.txt'):
            print('Parsing storage view file %s' % view)
            for line in FileUtil.readlines(view):
                cluster_name_m = cluster_name_re.search(line)
                if not cluster_name_m is None:
                    current_cluster_name = cluster_name_m.group(1)
                    current_cluster = cluster.objects.filter(cdlog_id=self.cdlog.id, name=current_cluster_name)[0]
                    current_cluster_id = current_cluster.id
                    current_cluster_directors = director.objects.filter(cluster_id=current_cluster.id)
                    current_cluster_directors_ids = [drct.id for drct in current_cluster_directors]
                    view_mapping_dict[current_cluster_id] = {}
                    continue
                view_name_m = view_name_re.search(line)
                if not view_name_m is None:
                    current_view_name = view_name_m.group(1)
                    continue
                view_status_m = view_status_re.search(line)
                if not view_status_m is None:
                    current_view_status = view_status_m.group(1)
                    current_storage_view = storage_view.objects.create(cluster_id=current_cluster.id, name=current_view_name, status=current_view_status)
                    current_storage_view_id = current_storage_view.id
                    view_mapping_dict[current_cluster_id][current_storage_view_id] = { 'mapping': {}, 'initiator_id': {}, 'port_id': {} }
                    continue
                view_initiator_title_m = view_initiator_title_re.search(line)
                if not view_initiator_title_m is None:
                    parsing_initiator = True
                    continue
                view_initiator_to_target_title_m = view_initiator_to_target_title_re.search(line)
                if not view_initiator_to_target_title_m is None:
                    parsing_initiator = False
                    parsing_initiator_to_target = True
                    continue
                view_ports_title_m = view_ports_title_re.search(line)
                if not view_ports_title_m is None:
                    parsing_initiator_to_target = False
                    parsing_port = True
                    continue
                if parsing_port and not empty_line_re.search(line) is None:
                    parsing_port = False
                    continue
                
                if parsing_initiator:
                    view_initiator_m = view_initiator_re.search(line)
                    if not view_initiator_m is None:
                        (initiator_name, wwnn, wwpn, host, logged_in, cross_connected) = view_initiator_m.groups()
                        current_initiator = view_initiator.objects.create(name=initiator_name, view_id=current_storage_view_id, wwnn=wwnn, wwpn=wwpn, host_type=host, logged_in=logged_in, cross_connected=cross_connected)
                        view_mapping_dict[current_cluster_id][current_storage_view_id]['initiator_id'][initiator_name] = current_initiator.id
                    continue
                if parsing_initiator_to_target:
                    view_initiator_to_target_m = view_initiator_to_target_re.search(line)
                    if not view_initiator_to_target_m is None:
                        (initiator_name, port_list) = view_initiator_to_target_m.groups()
                        view_mapping_dict[current_cluster_id][current_storage_view_id]['mapping'][initiator_name] = port_list.split(',')
                    continue
                if parsing_port:
                    if not view_port_re.search(line) is None:
                        for port_info in line.split(','):
                            if port_info != '':
                                port_m = view_port_re.search(port_info)
                                address = port_m.group(1)
                                port_identity = port_m.group(2)
                                current_port = port.objects.get(director_id__in=current_cluster_directors_ids, address=address)
                                port_id = current_port.id
                                view_port_obj = view_port.objects.create(view_id=current_storage_view_id, port_id=port_id)
                                view_port_id = view_port_obj.id
                                view_mapping_dict[current_cluster_id][current_storage_view_id]['port_id'][port_identity] = view_port_id
                    continue
            pass
            
        for cluster_id, views_info in view_mapping_dict.items():
            for view_id, view_info in views_info.items():
                mapping = view_info['mapping']
                initiator_dict = view_info['initiator_id']
                target_dict = view_info['port_id']
                for initiator_name, targets in mapping.items():
                    initiator_id = initiator_dict[initiator_name]
                    for port_identity in targets:
                        if port_identity in target_dict:
                            view_port_id = target_dict[port_identity]
                            login = view_initiator_target_login.objects.create(view_initiator_id=initiator_id, view_port_id=view_port_id)
                        pass
                    pass
                pass
            pass
    
    def parse_arrays(self):
        array_name_re = re.compile('^\s*Array\s+(\S+[\w\d])\s*$')
        vendor_re = re.compile('^\s*vendor\s+(\S+)\s*$')
        revision_re = re.compile('^\s*revision\s+(\S+)\s*$')
        connectivity_re = re.compile('i\s*:\s*(\S+)\s+t\s*:\s*(\S+)\s*$')
        
        current_array_name = None
        array_info = {}
        for array_file in self.walk_files('Array.txt'):
            print('Parsing array file %s...' % array_file)
            for line in FileUtil.readlines(array_file):
                array_name_m = array_name_re.search(line)
                if not array_name_m is None:
                    current_array_name = array_name_m.group(1)
                    array_info[current_array_name] = {}
                    array_info[current_array_name]['connectivities'] = []
                #   print(current_array_name)
                    continue
                if not current_array_name is None:
                    vendor_m = vendor_re.search(line)
                    if not vendor_m is None:
                        array_info[current_array_name]['vendor'] = vendor_m.group(1)
                        continue
                    revision_m = revision_re.search(line)
                    if not revision_m is None:
                        array_info[current_array_name]['revision'] = revision_m.group(1)
                        continue
                    connectivity_m = connectivity_re.search(line)
                    if not connectivity_m is None:
                        array_info[current_array_name]['connectivities'].append({ 'i': connectivity_m.group(1), 't': connectivity_m.group(2) })
                        continue
                        
    #   print(array_info)
        
        for array_name, array in array_info.items():
        #   print(array_name)
        #   print(array)
            storage_array_object = storage_array.objects.create(cdlog_id=self.cdlog.id, name=array_name, vendor=array['vendor'], revision=array['revision'])
            print('Dump array %s ...' % storage_array_object.name)
            storage_array_object_id = storage_array_object.id
            for connectivity_info in array['connectivities']:
                storage_array_connectivity_object = storage_array_connectivity.objects.create(storage_array_id=storage_array_object_id, i=connectivity_info['i'], t=connectivity_info['t'])
    
    def parse_firmwarelog(self):
        print('Parsing firmware log ...')
        for file in self.walk_files('firmware.log.merged'):
            cluster = 'N/A'
            print('Parsing firmware log %s' % file)
            fw_log_cluster_m = self.fw_log_cluster_regex.search(file)
            if not fw_log_cluster_m is None:
                cluster = fw_log_cluster_m.group(1)
                fwlog_handler = FirmwareLogHandler(cdlog_id=self.cdlog.id, cluster=cluster, file=file)
                fwlog_handler.parse()
        
    def parse_sys_perf_file_list(self):
        print('Parsing sys perf ...')
        remark_re_str = '(director-\d-\d-\w)_PERPETUAL_vplex_sys_perf_mon.log\.*(\d*)'
        remark_re = re.compile(remark_re_str)
        sys_perf_file_dict = {}
        for file in self.walk_files(remark_re_str):
            remark_m = remark_re.search(file)
            if not remark_m is None:
                director = remark_m.group(1)
                log_id = remark_m.group(2)
                if log_id == '':
                    log_id = '0'
            #   print('%s %s %s' % (director, log_id, file))
                if not director in sys_perf_file_dict:
                    sys_perf_file_dict[director] = {}
                if not log_id in sys_perf_file_dict[director]:
                    sys_perf_file_dict[director][log_id] = file
            else:
                print(file)
                
        directors = list(sys_perf_file_dict.keys())
        directors.sort()
        for director in directors:
            if director in self.director_name_dict:
                director_id = self.director_name_dict[director].id
                print('%s - %s' % (director, director_id))
                log_ids = list(sys_perf_file_dict[director].keys())
                log_ids.sort()
                for log_id in reversed(log_ids):
                    path = sys_perf_file_dict[director][log_id]
                    print('Dumping system performance file [%s] to database ...' % path)
                    SysPerfLog.objects.create(director_id=director_id, log_segment_id=log_id, path=path)

    def parse_vv_perf_file_list(self):
        print('Parsing vv perf ...')
        remark_re_str = '(director-\d-\d-\w)_VIRTUAL_VOLUMES_PERPETUAL_MONITOR.log\.?(\d*)'
        remark_re = re.compile(remark_re_str)
        vv_perf_file_dict = {}
        for file in self.walk_files(remark_re_str):
            remark_m = remark_re.search(file)
            if not remark_m is None:
                director = remark_m.group(1)
                log_id = remark_m.group(2)
                if log_id == '':
                    log_id = '0'
            #   print('%s %s %s' % (director, log_id, file))
                if not director in vv_perf_file_dict:
                    vv_perf_file_dict[director] = {}
                if not log_id in vv_perf_file_dict[director]:
                    vv_perf_file_dict[director][log_id] = file
            else:
                print(file)

        directors = list(vv_perf_file_dict.keys())
        directors.sort()
        for director in directors:
            if director in self.director_name_dict:
                director_id = self.director_name_dict[director].id
                print('%s - %s' % (director, director_id))
                log_ids = list(vv_perf_file_dict[director].keys())
                log_ids.sort()
                for log_id in reversed(log_ids):
                    path = vv_perf_file_dict[director][log_id]
                    csv_path = path + '.csv'
                    print('Dumping virtual volume performance file [%s] to database ...' % path)
                    PerformanceFileUtil.vv_log_to_csv(path, csv_path)
                    VVPerfLog.objects.create(director_id=director_id, log_segment_id=log_id, path=csv_path)
        pass
        
    def parse_tach_sh_login(self):
        current_engine = ''
        current_director = ''
        for file in LocalFolderUtil.walk_files(self.directory, 'debugTowerDump\S+'):
            for line in FileUtil.readlines_between_regex(file, '^\s*COMMAND tach sh login', '^\s*Total\s+logins\s*:\s*\d+'):
                print(line)
                eng_dir = REUtil.groups(line, '^\s*DIRECTOR /engines/(engine-\d-\d)/directors/(director-\d-\d-\w)')
                if eng_dir[0]:
                    current_engine = eng_dir[1][0]
                    current_director = eng_dir[1][1]
                else:
                    tach_sh_login_tx = REUtil.groups(line, '^\s*NPortID (\S+) state FC4READY type (INI|TGT) I (\S+) T (\S+)\s*$')
                    if tach_sh_login_tx[0]:
                        type = tach_sh_login_tx[1][1]
                        i = tach_sh_login_tx[1][2]
                        t = tach_sh_login_tx[1][3]
                        print('%s %s %s %s' % (current_engine, current_director, i, t))
                        tach_sh_login.objects.create(cdlog_id=self.cdlog.id, engine_name=current_engine, director_name=current_director, type=type, i=i, t=t)
                print()
        pass
        
    def parse_misc(self):
        self.parse_tach_sh_login()
        pass
        
    def parse(self):
        self.parse_cluster()
        self.parse_director()
        self.parse_ports()
        self.parse_storage_view()
        self.parse_arrays()
        self.parse_firmwarelog()
        self.parse_sys_perf_file_list()
        self.parse_vv_perf_file_list()
        self.parse_misc()
        pass