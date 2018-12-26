import ftplib
from ftplib import FTP
from functools import wraps
from datetime import datetime
import hashlib
import os
from os import path
import pandas as pd
import re
from django.db import connection

class HashUtil:
    @classmethod
    def md5_for_str(t, content):
        m = hashlib.md5()
        m.update(content)
        return m.hexdigest()

method_cacher = {}

def cache_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        key = f.__module__ + '_' + f.__name__ + '_' + str(args) + '_' + str(kwds)
        key_md5 = HashUtil.md5_for_str(key.encode('utf-8'))
        
        print('=====================Cache decorator=====================')
        print('Key:%s' % key)
        print('Key MD5:%s' % key_md5)
        
        result = None
        if not key_md5 in method_cacher:
            print('Miss...')
            print('Invoking backend method...')
            result = f(*args, **kwds)
            method_cacher[key_md5] = result
        else:
            print('Hit...')
            print('Reading from cache...')
            result = method_cacher[key_md5]
        print('=========================================================')
        return result
    return wrapper

class cached_pd:
    @cache_decorator
    def read_csv(file):
        return pd.read_csv(file)
        
class FTPUtil:
    def __init__(self, host, user, passwd):
        self.ftp = FTP(host=host, user=user, passwd=passwd)

    def cwd(self, path):
        self.ftp.cwd(path)
        
    def nlst(self):
        return self.ftp.nlst()
        
    def download_folder(self, remote_path, local_path = '.', white_list_regex = None, recursive = False):
        previous_remote_path = self.ftp.pwd()
        try:
            self.ftp.cwd('/' + remote_path)
        except ftplib.error_perm:
            print('Failed to download folder %s...' % remote_path)
            self.ftp.cwd(previous_remote_path)
            return

        local_path = path.join(local_path, path.basename(remote_path))
        LocalFolderUtil.create_if_not_exists(local_path)
        filelist = self.ftp.nlst()
        for file in filelist:
            sub_remote_path = path.join(remote_path, file)
            sub_local_path = path.join(local_path, file)
            try:
                self.ftp.cwd(file)
                if recursive:
                    self.download_folder(sub_remote_path, local_path, white_list_regex, recursive)
                self.ftp.cwd('..')
            except ftplib.error_perm:
                try:
                    if (white_list_regex is None) or (not white_list_regex.search(file) is None):
                        print('Downloading %s as %s...' % (sub_remote_path, sub_local_path))
                        self.ftp.retrbinary('RETR ' + file, open(sub_local_path, "wb").write)
                    else:
                        print('Skip %s...' % file)
                except ftplib.error_perm:
                    print('Failed to download %s...' % sub_remote_path)
        self.ftp.cwd(previous_remote_path)
        
    def download_file(self, remote_file, local_file):
        self.ftp.retrbinary('RETR ' + remote_file, open(path.join(local_file, path.basename(remote_file)), "wb").write)

class LocalFolderUtil:
    @classmethod
    def create_if_not_exists(type, directory):
        if not path.exists(directory):
            os.makedirs(directory)

    @classmethod
    def get_folder_size(type, start_path = '.'):
        total_size = 0
    #   print(start_path)
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                current_size = os.path.getsize(fp)
            #   print('%s - %s' % (fp, current_size))
                total_size += current_size
        return total_size

    @classmethod
    def walk_files(type, directory, file):
        matches = []
        file_re = re.compile(file)
        for (root, dirs, files) in os.walk(directory):
            if file in files:
                matches.append(path.join(root, file))
            else:
                for f in files:
                    if file_re.search(f):
                        matches.append(path.join(root, f))
        return matches

class CDLogDownloader:
    def __init__(self, host, user, passwd):
        self.ftp_util = FTPUtil(host, user, passwd)

    def thin_download(self, remote_path, local_path):
        local_extracted_folder = path.join(local_path, path.basename(remote_path))
        LocalFolderUtil.create_if_not_exists(local_extracted_folder)

    #   self.ftp_util.download_folder(remote_path=remote_path, local_path=local_path, recursive=True)
        self.ftp_util.download_folder(remote_path=path.join(remote_path, 'analysisnotes'), local_path=local_extracted_folder, recursive=False)
        self.ftp_util.download_file(remote_file=path.join(remote_path, 'AnalysisNotes.html'), local_file=local_extracted_folder)
        LocalFolderUtil.create_if_not_exists(path.join(local_extracted_folder, 'mgmt_server'))
        for cluster_id in range(1, 3):
            LocalFolderUtil.create_if_not_exists(path.join(local_extracted_folder, 'mgmt_server/cluster-%s/' % cluster_id))
            self.ftp_util.download_folder(remote_path=path.join(remote_path, 'mgmt_server/cluster-%s/clilogs' % cluster_id), \
                                            local_path=path.join(local_extracted_folder, 'mgmt_server/cluster-%s/' % cluster_id), \
                                            white_list_regex = re.compile('(log.merged|PERPETUAL.*?log)'), \
                                            recursive=False)
        pass
        
    def full_download(self, remote_path, local_path):
        local_extracted_folder = path.join(local_path, path.basename(remote_path))
        LocalFolderUtil.create_if_not_exists(local_extracted_folder)

        self.ftp_util.download_folder(remote_path=remote_path, local_path=local_path, recursive=True)
        pass
        
    def download(self, remote_path, local_path, thin = True):
        if thin:
            self.thin_download(remote_path, local_path)
        else:
            self.full_download(remote_path, local_path)
            
class REUtil:
    @classmethod
    def is_match(t, content, re_str):
        re_obj = re.compile(re_str)
        return not re_obj.search(content) is None
        
    @classmethod
    def groups(t, content, re_str):
        result = []
        re_obj = re.compile(re_str)
        m = re_obj.search(content)
        if m:
            result.append(True)
            result.append(list(m.groups()))
        else:
            result.append(False)
        return result

class FileUtil:
    @classmethod
    def readlines(t, file):
        lines = []
        with open(file) as f:
            lines = [line.rstrip() for line in f.readlines()]
        f.close()
        return lines

    @classmethod
    def readlines_between_regex(t, file, start_re, end_re):
        s_re = re.compile(start_re)
        e_re = re.compile(end_re)
        started = False
        lines = []
        picked_lines = []
        with open(file) as f:
            lines = [line.rstrip() for line in f.readlines()]
        f.close()
        for line in lines:
            if not started:
                if s_re.search(line):
                    started = True
            if started:
                picked_lines.append(line)
                if e_re.search(line):
                    break
        return picked_lines
        
class SQLUtil:
    @classmethod
    def execute_sql(t, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            
    @classmethod
    def execute_sql_rows(t, sql):
        print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
            
    @classmethod
    def execute_sql_scalar(t, sql):
        return SQLUtil.execute_sql_rows(sql)[0][0]

class SafeConvertUtil:
    @classmethod
    def to_float(t, value):
        result = 0.0
        try:
            result = float(value)
        except:
            print('Unable to parse %s to float, will use 0.0 instead.' % value)
        return result

class PerformanceFileUtil:
    @classmethod
    def vv_log_to_csv(t, log_file, csv_file, overwritting=False):
        if not overwritting and path.exists(csv_file):
            print('%s exists, skip formatting...' % csv_file)
            return
        
        datetime_r = re.compile('^\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)\s*$')
        current_datetime = None
        current_line = None
        formated_lines = []
        formated_content = []

        for line in FileUtil.readlines(log_file):
            datetime_m = datetime_r.search(line)
            if not datetime_m is None:
                current_datetime = datetime_m.group(0)
                current_datetime_utc = datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S').timestamp() * 1000
                continue
            if current_datetime is None:
                current_line = 'Time (UTC),Time,' + line
            else:
                current_line = '%s,%s,%s' % (current_datetime_utc, current_datetime, line)
            formated_lines.append(current_line)

        formated_content = "\n".join(formated_lines)

        if csv_file is None:
            csv_file = log_file + '.csv'

        with open(csv_file, 'w') as o:
            o.write(formated_content)
        print('%s generated...' % csv_file)
        return csv_file
        pass

    @classmethod
    def vv_log_dir_to_csv_dir(t, log_dir):
        csv_files = []
        for vv_perf_log in LocalFolderUtil.walk_files(log_dir, '^director-\d-\d-\w_VIRTUAL_VOLUMES_PERPETUAL_MONITOR.log\.?\d?$'):
            vv_perf_csv = vv_perf_log + '.csv'
            csv_files.append(vv_perf_csv)
            PerformanceFileUtil.vv_log_to_csv(vv_perf_log, vv_perf_csv, overwritting=False)
        return csv_files
        pass

class log_extract_jobstate(object):
    NOT_STARTED = "NOT_STARTED"
    PICKED = "PICKED"
    RUNNING = "RUNNING"
    COMPLETED_SUCCEEDED = "COMPLETED_SUCCEEDED"
    COMPLETED_FAILED = "COMPLETED_FAILED"
