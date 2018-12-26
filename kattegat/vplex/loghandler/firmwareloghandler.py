import re
import pytz
from datetime import datetime
from ..models import Investigation, FirmwareLog, FirmwareLogEntry
from .loghandler import LogHandler

class FirmwareLogHandler(LogHandler):
    def __init__(self, cdlog_id, cluster, file):
        self.cdlog_id = cdlog_id
        self.cluster = cluster
        self.file = file

    stdf10_regex = re.compile('\[(\S.+?)\]\s+.+?\s+\[(\S+)\s+\((\S+)\)\s+(\S+)\s+\((\S+)\).+?\]\s+vol\s+(\S+)')
    def stdf10(self, element_dict):
        stdf10_m = self.stdf10_regex.search(element_dict['content'])
        if not stdf10_m is None:
            element_dict['sub_desc'] = stdf10_m.group(1)
            element_dict['i_port_name'] = stdf10_m.group(2)
            element_dict['i_port'] = stdf10_m.group(3)
            element_dict['t_port_name'] = stdf10_m.group(4)
            element_dict['t_port'] = stdf10_m.group(5)
            element_dict['vv_name'] = stdf10_m.group(6)
            return True
        else:
            return False
        pass
        
    amf249_250_regex = re.compile('^Amf\s+(\S+)\s+performance\s+')
    def amf249_250(self, element_dict):
        amf249_250_m = self.amf249_250_regex.search(element_dict['content'])
        if not amf249_250_m is None:
            element_dict['vv_name'] = amf249_250_m.group(1)
            return True
        else:
            return False
        pass

    scsi27_tgt_regex = re.compile('tgt\s+(\S+)\s+cmd\s+(\S+)\s+.*?asc\s+(\S+)\s+ascq\s+(\S+)')
    scsi27_i_t_regex = re.compile('tgt\s+x\s+\S+\s+i\s+(\S+)\s+t\s+(\S+).+?\s+cmd\s+(\S+)\s+.*?asc\s+(\S+)\s+ascq\s+(\S+)')
    def scsi27(self, element_dict):
        scsi27_tgt_m = self.scsi27_tgt_regex.search(element_dict['content'])
        if not scsi27_tgt_m is None:
            element_dict['sv_uuid'] = scsi27_tgt_m.group(1)
            element_dict['scsi_cmd'] = scsi27_tgt_m.group(2)
            element_dict['asc'] = scsi27_tgt_m.group(3)
            element_dict['ascq'] = scsi27_tgt_m.group(4)
            return True
        scsi27_i_t_m = self.scsi27_i_t_regex.search(element_dict['content'])
        if not scsi27_i_t_m is None:
            element_dict['i_port'] = scsi27_i_t_m.group(1)
            element_dict['t_port'] = scsi27_i_t_m.group(2)
            element_dict['scsi_cmd'] = scsi27_i_t_m.group(3)
            element_dict['asc'] = scsi27_i_t_m.group(4)
            element_dict['ascq'] = scsi27_i_t_m.group(5)
            return True
        return False
        pass

    scsi155_regex = re.compile('Scsi\s+command\s+(\S+).*?luid\s+(\S+)', re.IGNORECASE)
    def scsi155(self, element_dict):
        scsi155_m = self.scsi155_regex.search(element_dict['content'])
        if not scsi155_m is None:
            element_dict['scsi_cmd'] = scsi155_m.group(1)
            element_dict['sv_uuid'] = scsi155_m.group(2)
            return True
        return False
        pass
        
    disk1004_disk_regex = re.compile('found disk (\S+)')
    def disk1004(self, element_dict):
        disk1004_disk_m = self.disk1004_disk_regex.search(element_dict['content'])
        if not disk1004_disk_m is None:
            element_dict['sv_name'] = disk1004_disk_m.group(1)
            return True
        return False
        pass
        
    tach37_38_regex = re.compile('^\s*\S+\s+\(\s*(\S+)\s*\)\s*:\s*login\s+with\s+(\S+)')
    def tach37_38(self, element_dict):
        tach37_38_m = self.tach37_38_regex.search(element_dict['content'])
        if not tach37_38_m is None:
            element_dict['t_port_name'] = tach37_38_m.group(1)
            element_dict['i_port'] = tach37_38_m.group(2)
            return True
        return False
        pass
        
    specific_event_methods = { \
                            'stdf': { \
                                    10: stdf10, \
                                }, \
                            'amf': { \
                                    249: amf249_250, \
                                    250: amf249_250, \
                                }, \
                            'scsi': { \
                                    27: scsi27, \
                                    155: scsi155, \
                                }, \
                            'disk': { \
                                    1004: disk1004, \
                                }, \
                            'tach': { \
                                    37: tach37_38, \
                                    38: tach37_38, \
                                }, \
                            }

    def parse_specific_event(self, element_dict):
        component = element_dict['component']
        event_id = element_dict['event_id']
        if component in self.specific_event_methods and event_id in self.specific_event_methods[component]:
            if not self.specific_event_methods[component][event_id](self, element_dict):
                raise RuntimeError('%s/%s failed to be parse by specific event handler! Raw text as [%s]...' % (component, event_id, element_dict['content']))
        pass

    chunk_trim_regex = re.compile('^.*?(\'|\")(.*?)(\'|\")$')
    main_regex = re.compile('^\d+\.\d+\.\d+\.(\d+)\S+?(\d+)\/(\d+)\/(\d+)\s+(\d+):(\d+):(\d+)\.\d+:\s+(\S+?)\/(\d+)\s+(\S.+?)\s*$')
    i_t_regex = re.compile('\s+i\s+(\S+)\s+t\s+(\S+?)\W+')
    ip_dir_dict = { 35: 'director-1-1-A', \
                    36: 'director-1-1-B', \
                    37: 'director-1-2-A', \
                    38: 'director-1-2-B', \
                    39: 'director-1-3-A', \
                    40: 'director-1-3-B', \
                    41: 'director-1-4-A', \
                    42: 'director-1-4-B', \
                    67: 'director-2-1-A', \
                    68: 'director-2-1-B', \
                    69: 'director-2-2-A', \
                    70: 'director-2-2-B', \
                    71: 'director-2-3-A', \
                    72: 'director-2-3-B', \
                    73: 'director-2-4-A', \
                    74: 'director-2-4-B', }
    
    def parse(self):
        content = ''
        
        fp = open(self.file, "r")
        self.log_entries = []
        for line in list(fp):
#           print(line)
            main_m = self.main_regex.match(line)
            if not main_m is None:
#               print("%s %s %s %s %s %s %s %s %s" % \
#                   (main_m.group(1), main_m.group(2), main_m.group(3), \
#                   main_m.group(4), main_m.group(5), main_m.group(6), \
#                   main_m.group(7), main_m.group(8), main_m.group(9)))
                main_element_dict = {}
                main_element_dict['ip'] = main_m.group(1)
                main_element_dict['director'] = self.ip_dir_dict[int(main_element_dict['ip'])]
                main_element_dict['year'] = main_m.group(2)
                main_element_dict['month'] = main_m.group(3)
                main_element_dict['day'] = main_m.group(4)
                main_element_dict['hour'] = main_m.group(5)
                main_element_dict['minute'] = main_m.group(6)
                main_element_dict['second'] = main_m.group(7)
                main_element_dict['date_time'] = datetime(int(main_element_dict['year']), \
                                                            int(main_element_dict['month']), \
                                                            int(main_element_dict['day']), \
                                                            int(main_element_dict['hour']), \
                                                            int(main_element_dict['minute']), \
                                                            int(main_element_dict['second']), \
                                                            0, \
                                                            tzinfo=pytz.UTC)
                main_element_dict['component'] = main_m.group(8)
                main_element_dict['event_id'] = int(main_m.group(9))
                main_element_dict['content'] = main_m.group(10)
                main_element_dict['text'] = line
                
                i_t_m = self.i_t_regex.search(main_element_dict['content'])
                if not i_t_m is None:
                    main_element_dict['i_port'] = i_t_m.group(1)
                    main_element_dict['t_port'] = i_t_m.group(2)

                self.parse_specific_event(main_element_dict)
            
                #FirmwareLog.objects.create()
                log_entry = FirmwareLogEntry()
                for col in main_element_dict:
                    setattr(log_entry, col, main_element_dict[col])
                self.log_entries.append(log_entry)
    #           else:
    #               raise RuntimeError
                pass

        firmwarelog = FirmwareLog.objects.create(cluster=self.cluster, cdlog_id=self.cdlog_id, filepath=self.file)
        firmwarelog_id = firmwarelog.id
        for log_entry in self.log_entries:
            log_entry.firmwarelog_id = firmwarelog_id
        len_log_entries = len(self.log_entries)
        step = 10000
        for start in range(0, len_log_entries, step):
            end = 0
            if start + step > len_log_entries:
                end = len_log_entries
            else:
                end = start + step - 1
            FirmwareLogEntry.objects.bulk_create(self.log_entries[start:end])
            print('%s to %s dumpped.' % (start, end))
        pass
