from django.db import models
from datetime import datetime
from .utils import log_extract_jobstate

# Create your models here.
class Investigation(models.Model):
    id = models.AutoField(primary_key=True)
    sr_id = models.IntegerField()
    sr_oracle_id = models.IntegerField(null=True)
    owner = models.CharField(max_length=100)
    description = models.CharField(max_length=1500, null=True)
    date_time = models.DateTimeField(auto_now=True)

class CDLog(models.Model):
    id = models.AutoField(primary_key=True)
    investigation_id = models.IntegerField(null=False)
    serial_number = models.CharField(default='N/A', max_length=100)
    code_level = models.CharField(default='N/A', max_length=100)
    product_type = models.CharField(default='N/A', max_length=100)
    hardware_type = models.CharField(default='N/A', max_length=100)
    remote_directory = models.CharField(default='N/A', max_length=500)
    local_directory = models.CharField(default='N/A', max_length=500)
    download_started = models.BooleanField(default=False)
    download_completed = models.BooleanField(default=False)
    download_succeeded = models.BooleanField(default=False)
    dump_started = models.BooleanField(default=False)
    dump_completed = models.BooleanField(default=False)
    dump_succeeded = models.BooleanField(default=False)
    exception = models.CharField(default='N/A', max_length=3000)
    date_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.serial_number

class CDLog_Extraction_Job(models.Model):
    id = models.AutoField(primary_key=True)
    cdlog_id = models.IntegerField(null=False, default=-1)
    cdlog_file = models.CharField(default='N/A', max_length=1000)
    extracted_folder = models.CharField(default='N/A', max_length=1000)
    state = models.CharField(default=log_extract_jobstate.NOT_STARTED, max_length=100)
    returncode = models.IntegerField(null=False, default=0)
    exception = models.CharField(null=False, default='', max_length=1000)
    owner = models.CharField(null=False, default='N/A', max_length=500)
        
class cluster(models.Model):
    id = models.AutoField(primary_key=True)
    cdlog_id = models.IntegerField(null=False)
    name = models.CharField(default='N/A', max_length=100)
    serial_number = models.CharField(default='N/A', max_length=100)
        
class director(models.Model):
    id = models.AutoField(primary_key=True)
    cluster_id = models.IntegerField(null=False)
    name = models.CharField(default='N/A', max_length=100)
    ip = models.CharField(default='N/A', max_length=100)
    uid = models.CharField(default='N/A', max_length=100)
    
class tach_sh_login(models.Model):
    id = models.AutoField(primary_key=True)
    cdlog_id = models.IntegerField(null=False)
    engine_name = models.CharField(default='N/A', max_length=100)
    director_name = models.CharField(default='N/A', max_length=100)
    type = models.CharField(default='N/A', max_length=3)
    i = models.CharField(default='N/A', max_length=50)
    t = models.CharField(default='N/A', max_length=50)
    
class port(models.Model):
    id = models.AutoField(primary_key=True)
    director_id = models.IntegerField(null=False)
    name = models.CharField(default='N/A', max_length=30)
    address = models.CharField(default='N/A', max_length=100)
    role = models.CharField(default='N/A', max_length=50)
    status = models.CharField(default='N/A', max_length=30)
    
class sfps(models.Model):
    id = models.AutoField(primary_key=True)
    port_id = models.IntegerField(null=False)
    name = models.CharField(default='N/A', max_length=30)
    manufacturer = models.CharField(default='N/A', max_length=50)
    part_number = models.CharField(default='N/A', max_length=50)
    serial_number = models.CharField(default='N/A', max_length=50)
    rx_power = models.IntegerField(null=True)
    tx_power = models.IntegerField(null=True)
    temprature = models.IntegerField(null=True)
        
class storage_view(models.Model):
    id = models.AutoField(primary_key=True)
    cluster_id = models.IntegerField(null=False)
    name = models.CharField(default='N/A', max_length=50)
    status = models.CharField(default='N/A', max_length=30)
    
class view_initiator(models.Model):
    id = models.AutoField(primary_key=True)
    view_id = models.IntegerField(null=False, default=-1)
    name = models.CharField(default='N/A', max_length=50)
    wwnn = models.CharField(default='N/A', max_length=100)
    wwpn = models.CharField(default='N/A', max_length=100)
    host_type = models.CharField(default='N/A', max_length=100)
    logged_in = models.CharField(default='N/A', max_length=100)
    cross_connected = models.CharField(default='N/A', max_length=100)
    
class view_port(models.Model):
    id = models.AutoField(primary_key=True)
    view_id = models.IntegerField(null=False, default=-1)
    port_id = models.IntegerField(null=False, default=-1)
    
class view_initiator_target_login(models.Model):
    id = models.AutoField(primary_key=True)
    view_initiator_id = models.IntegerField(null=False)
    view_port_id = models.IntegerField(null=False)
        
class storage_array(models.Model):
    id = models.AutoField(primary_key=True)
    cdlog_id = models.IntegerField(null=False, default=-1)
    name = models.CharField(default='N/A', max_length=50)
    vendor = models.CharField(default='N/A', max_length=30)
    revision = models.CharField(default='N/A', max_length=30)
        
class storage_array_connectivity(models.Model):
    id = models.AutoField(primary_key=True)
    storage_array_id = models.IntegerField(null=False, default=-1)
    i = models.CharField(default='N/A', max_length=150)
    t = models.CharField(default='N/A', max_length=150)
        
class FirmwareLog(models.Model):
    id = models.AutoField(primary_key=True)
    cluster = models.CharField(default='N/A', max_length=30)
    cdlog_id = models.IntegerField(null=False)
    filepath = models.CharField(default='', max_length=500)
        
class FirmwareLogEntry(models.Model):
    id = models.AutoField(primary_key=True)
    firmwarelog_id = models.IntegerField(null=False)
    text = models.CharField(max_length=5000)
    ip = models.CharField(default='N/A', max_length=100)
    director = models.CharField(default='N/A', max_length=50)
    year = models.IntegerField(default=-1)
    month = models.IntegerField(default=-1)
    day = models.IntegerField(default=-1)
    hour = models.IntegerField(default=-1)
    minute = models.IntegerField(default=-1)
    second = models.IntegerField(default=-1)
    date_time = models.DateTimeField(null=False, default=datetime(1, 1, 1, 0, 0, 0))
    component = models.CharField(default='N/A', max_length=30)
    event_id = models.IntegerField(default=-1)
    i_port_name = models.CharField(default='N/A', max_length=100)
    i_port = models.CharField(default='N/A', max_length=100)
    t_port_name = models.CharField(default='N/A', max_length=100)
    t_port = models.CharField(default='N/A', max_length=100)

'''
sub_desc = models.CharField(default='N/A', max_length=100)
vv_name = models.CharField(default='N/A', max_length=100)
vv_uuid = models.CharField(default='N/A', max_length=100)
sv_name = models.CharField(default='N/A', max_length=100)
sv_uuid = models.CharField(default='N/A', max_length=100)
scsi_cmd = models.CharField(default='N/A', max_length=30)
asc = models.CharField(default='N/A', max_length=10)
ascq = models.CharField(default='N/A', max_length=10)
'''

class SysPerfLog(models.Model):
    id = models.AutoField(primary_key=True)
    director_id = models.IntegerField(default=-1)
    log_segment_id = models.IntegerField(default=-1)
    path = models.CharField(default='N/A', max_length=600)

class VVPerfLog(models.Model):
    id = models.AutoField(primary_key=True)
    director_id = models.IntegerField(default=-1)
    log_segment_id = models.IntegerField(default=-1)
    path = models.CharField(default='N/A', max_length=600)

class FirmwareLogEventCode(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.CharField(default='N/A', max_length=50)
    component = models.CharField(default='N/A', max_length=50)
    code = models.IntegerField(default=-1)
    internalRCA = models.CharField(default='N/A', max_length=3000)
    customerRCA = models.CharField(default='N/A', max_length=3000)
    customerDescription = models.CharField(default='N/A', max_length=3000)
    formatString = models.CharField(default='N/A', max_length=3000)
    
    @classmethod
    def event_rca_dict(t):
        dict = {}
        with connection.cursor() as cursor:
            sql = 'SELECT component, code, version, internalRCA, customerRCA, formatString, customerDescription FROM firmware_log_event_code'
            cursor.execute(sql)
            for row in cursor.fetchall():
                component = row[0]
                code = row[1]
                version = row[2]
                internalRCA = row[3]
                customerRCA = row[4]
                formatString = row[5]
                customerDescription = row[6]
                if not component in dict:
                    dict[component] = {}
                if not code in dict[component]:
                    dict[component][code] = {}
                if not version in dict[component][code]:
                    dict[component][code][version] = 'Internal RCA : ' + internalRCA + '\nCustomer RCA : ' + customerRCA + '\nDescription : ' + formatString + '\nInternal description : ' + customerDescription
        return dict
        pass

    @classmethod
    def all_group_columns(t):
        return ['ip', 'director', 'year', 'month', 'day', 'hour', 'minute', 'i_port', 't_port', 'i_port_name', 't_port_name', 'sv_uuid', 'sv_name', 'vv_uuid', 'vv_name', 'sub_desc', 'scsi_cmd', 'asc', 'ascq']
        
    @classmethod
    def group_by_columns(t, investigation_id, component, code, group_columns, start_date_time, end_date_time):
        group_columns_str = None
        if group_columns is None or len(group_columns) == 0:
            group_columns = ['year', 'month', 'day']
        group_columns_str = '`' + '`, `'.join(group_columns) + '`'
        headers = group_columns
        headers.insert(0, 'count')
        headers = tuple(headers)
        sql = 'SELECT COUNT(*), %s FROM firmware_log_firmwarelog WHERE investigation_id = %s AND component = \'%s\' AND event_id = %s AND date_time >= \'%s\' AND date_time <= \'%s\' GROUP BY %s' % \
                (group_columns_str, investigation_id, component, code, start_date_time, end_date_time, group_columns_str)
        rows = []
        with connection.cursor() as cursor:
            print(sql)
            cursor.execute(sql)
            rows = list(cursor.fetchall())
        return {'headers': headers, 'rows': rows}
        pass
        
class event_code(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.CharField(default='N/A', max_length=50)
    component = models.CharField(default='N/A', max_length=50)
    code = models.IntegerField(default=-1)
    internalRCA = models.CharField(default='N/A', max_length=3000)
    customerRCA = models.CharField(default='N/A', max_length=3000)
    customerDescription = models.CharField(default='N/A', max_length=3000)
    formatString = models.CharField(default='N/A', max_length=3000)
    
    @classmethod
    def event_rca_dict(t):
        dict = {}
        with connection.cursor() as cursor:
            sql = 'SELECT component, code, version, internalRCA, customerRCA, formatString, customerDescription FROM firmware_log_event_code'
            cursor.execute(sql)
            for row in cursor.fetchall():
                component = row[0]
                code = row[1]
                version = row[2]
                internalRCA = row[3]
                customerRCA = row[4]
                formatString = row[5]
                customerDescription = row[6]
                if not component in dict:
                    dict[component] = {}
                if not code in dict[component]:
                    dict[component][code] = {}
                if not version in dict[component][code]:
                    dict[component][code][version] = 'Internal RCA : ' + internalRCA + '\nCustomer RCA : ' + customerRCA + '\nDescription : ' + formatString + '\nInternal description : ' + customerDescription
        return dict
        pass

    @classmethod
    def all_group_columns(t):
        return ['ip', 'director', 'year', 'month', 'day', 'hour', 'minute', 'i_port', 't_port', 'i_port_name', 't_port_name', 'sv_uuid', 'sv_name', 'vv_uuid', 'vv_name', 'sub_desc', 'scsi_cmd', 'asc', 'ascq']
        
    @classmethod
    def group_by_columns(t, investigation_id, component, code, group_columns, start_date_time, end_date_time):
        group_columns_str = None
        if group_columns is None or len(group_columns) == 0:
            group_columns = ['year', 'month', 'day']
        group_columns_str = '`' + '`, `'.join(group_columns) + '`'
        headers = group_columns
        headers.insert(0, 'count')
        headers = tuple(headers)
        sql = 'SELECT COUNT(*), %s FROM firmware_log_firmwarelog WHERE investigation_id = %s AND component = \'%s\' AND event_id = %s AND date_time >= \'%s\' AND date_time <= \'%s\' GROUP BY %s' % \
                (group_columns_str, investigation_id, component, code, start_date_time, end_date_time, group_columns_str)
        rows = []
        with connection.cursor() as cursor:
            print(sql)
            cursor.execute(sql)
            rows = list(cursor.fetchall())
        return {'headers': headers, 'rows': rows}
        pass