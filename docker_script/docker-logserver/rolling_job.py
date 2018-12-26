import os
import shutil
import sys
import time
import MySQLdb as sql
import subprocess

def get_cursor():
    return sql.connect(host=os.environ['DB_CONTAINER_NAME'], user='vplex_log_db_access', password='VPlex_1234567890', db='vplex_log')

def hostname():
    return subprocess.check_output(("hostname"))
    
def get_standby_job_list():
    standby_jobs = ()
    with get_cursor() as cursor:
        cursor.execute('select * from vplex_cdlog_extraction_job where state = \'NOT_STARTED\'')
        standby_jobs = cursor.fetchall()
        cursor.close()
    return standby_jobs

def pick_job(job_id, host_name):
    with get_cursor() as cursor:
        cursor.execute('update vplex_cdlog_extraction_job set state = \'PICKED\', owner = \'%s\' where id = %s' % (host_name, job_id))
        cursor.close()

def extract_log(job_id, file_path):
    returncode = -1
    extracted_directory = file_path.replace('.tar.gz', '')
    try:
        with get_cursor() as cursor:
            host_name = hostname()
            cursor.execute("select * from vplex_cdlog_extraction_job where id = %s and owner = \'%s\'" % (job_id, host_name))
            if len(cursor.fetchall()) == 0:
                print 'Job with id %s has been taken by other container, exit...'
                cursor.close()
                return
            cursor.close()
        with get_cursor() as cursor:
            cursor.execute('update vplex_cdlog_extraction_job set state = \'RUNNING\' where id = %s' % job_id)
            cursor.close()
        if os.path.exists(extracted_directory):
            shutil.rmtree(extracted_directory)
        returncode = subprocess.call(("/LogAnalysis/logAnalysisTool.sh", "-l", "/tmp/log.txt", file_path))
        status = 'COMPLETED_SUCCEEDED'
        if returncode != 0:
            status = 'COMPLETED_FAILED'
        with get_cursor() as cursor:
            cursor.execute('update vplex_cdlog_extraction_job set state = \'%s\' where id = %s' % (status, job_id))
            cursor.close()
    except:
        with get_cursor() as cursor:
            cursor.execute('update vplex_cdlog_extraction_job set state = \'COMPLETED_FAILED\' where id = %s' % job_id)
            cursor.close()
            (exc_info, exc_value, exc_stacktrace) = sys.exc_info()
            exception_str = str(exc_info) + " | " + str(exc_value) + " | " + str(exc_stacktrace)
            print exception_str
        with get_cursor() as cursor:
#           sql = 'update vplex_cdlog_extraction_job set exception = \'%s\' where id = %s' % (exception_str.replace('\'', '\'\''), job_id)
#           print '=============================================='
#           print sql
#           print '++++++++++++++++++++++++++++++++++++++++++++++'
            cursor.execute('update vplex_cdlog_extraction_job set exception = \'%s\' where id = %s' % (exception_str.replace('\'', '\'\''), job_id))
            cursor.close()
    finally:
        print '-------------------------------------'
        print returncode
        print '+++++++++++++++++++++++++++++++++++++'
        with get_cursor() as cursor:
            cursor.execute('update vplex_cdlog_extraction_job set returncode = %s where id = %s' % (returncode, job_id))
            cursor.close()
    return returncode

while(True):
    print 'Rolling...'
    standby_jobs = get_standby_job_list()
    for row in standby_jobs:
        job_id = row[0]
        log_file = row[1]
        extract_path = row[2]
        state = row[3]
        cdlog_id = row[4]
        host_name = hostname()
        pick_job(job_id, host_name)
        extract_ps_code = extract_log(job_id, log_file)
        if extract_ps_code == 0:
            print 'Successfully extracted %s...' % log_file
        else:
            print 'Failed to extract %s...' % log_file
    time.sleep(1)
