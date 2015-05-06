#!/usr/bin/python
from email.mime.text import MIMEText
from time import sleep
import subprocess
import datetime
import smtplib
import sys
import os
import re

class utils:
    
    def __init__(self, src, dst, src_host):
        self.source_dir = src
        self.source_host = src_host
        self.destination_dir = dst
    
    def ping(self):
        
        cmd = ('ping -c 3 %s' % self.source_host)
        
        ping = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = ping.stdout.read()
        err = ping.stderr.read()
    
        if output: #BAD BAD BAD, REWORK ALL BELOW!! LATENCY IS BROKEN - REDO LOGIC
            ping_latency = 0
            result = output.split('\n')
            for i in result:
                match = re.search(r'time=\w+.\w+', i)
                if match:
                    raw_latency = re.search(r'\d+.\d+', match.group())
                    x = raw_latency.group()
                    x =float(x)
                    ping_latency += x
                else:
                    pass
            
            self.ping_latency = ping_latency / 3
            
            #RETURN VALUES
            return True
             
        if err:
            self.ping_error = err
            
            #RETURN VALUES
            return False


    def mount(self, dirPath): 
        try:
            if os.path.ismount(dirPath): #If it's mounted.
                return True
            else: #If it's not mounted.
                try:
                    print('[!] Source mount point (%s) not found.' % dirPath)
                    print('[?] Attempting repair...')
                    os.system('mount -a')#Try "mount -a" to re-mount.
                    if os.path.ismount(dirPath):#Check if mounted after repair attempt.
                        print('[+] Source mount point (%s) has been repaired.' % dirPath)
                        return True
                    else:
                        return False                
                except IOError as e:
                    #EMAIL ALERT
                    print e
        except IOError as e:
            #SEND EMAIL
            print e
            
    
    #DST DIRECTORY CHECK FUNCTION - ENSURE LOCAL DIR EXISTS, IF NOT ATTEMPT REPAIR.
    def path(self):
        try:
            if os.path.exists(self.destination_dir):
                return True
            else:
                print("[!] Destination (%s) not found." % self.destination_dir)
                print("[?] Attempting to repair...")
                
                try:
                    os.mkdir(self.destination_dir)
                    return True
                except:
                    print("[!] Unable to repair destination (%s). Exiting script." % self.destination_dir)
                    return False                
        except IOError as e:
            print e
    
    def space(self, location):
        
        cmd = ('df -h %s' % location)
        try:
            df = subprocess.Popen([cmd], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = df.communicate()
            
            if stdout:
                output = stdout.split('\n')
                for line in output:
                    
                    items = re.findall(r'\d+\w\s', line)
                    posto = re.findall(r'\d+%', line)
                    
                    if items:
                        if len(items) != 3:
                            print ("[!] Unable to retrieve disc statistics!")
                            print ("[!] Failed collecting size, used, avail values.")
                            
                            #ERROR DETECTED
                            return False
                        else:
                            (size, used, avail) = items
                    
                    if posto:
                        if len(posto) != 1:
                            print ("[!] Unable to retrieve disc statistics!")
                            print ("[!] Failed collecting percent value.")
                            
                            #ERROR DETECTED
                            return False
                        else:
                            percent = posto[0]
                
                self.space_size = size
                self.space_used = used
                self.space_avail = avail
                self.space_percent = percent
            
                return True
    
            if stderr:
                self.space_error = stderr
                return False
                
        except IOError as e:
            print e
    
            
    def crypto(self, dirPath):
        
        crypto_ext = ('crypto', 'encrypted','decrypt','decrypt_instruction','_INSTRUCTION', 'cryptolocker', 'locker')

        self.crypto_count_clean = 0
        self.crypto_count_infected = 0
        
        dirtyFiles = ''
        
        try:
            if os.path.exists(dirPath):
                for dirName, subdirList, fileList in os.walk(dirPath):
                    for fname in fileList:
                        for ext in crypto_ext:
                            if re.search(ext, fname.lower()):
                                self.crypto_count_infected += 1
                                dirtyFiles += (dirName + '/' + fname + ',')
                            else:
                                pass
                        self.crypto_count_clean += 1
                                
                if self.crypto_count_infected > 0:
                    
                    #LIST OF INFECTED FILES
                    self.crypto_infected_files = dirtyFiles.split(',')
                    
                    #INFECTION FOUND
                    return False

                else:
                    #LIST OF INFECTED FILES SET TO NONE
                    self.crypto_infected_files = 'None'
                    
                    #INFECTION NOT FOUND
                    return True
                
            else:
                self.crypto_error = ("CryptoCheck(): Source path was not found")
                return False
                
        except IOError as e:
            print e

    #EMAIL ALERT + WITH A LOG FILE INCLUDED
    def mail(self, status):
        
        try:
            msg = MIMEText('Testing email')
            
            msg['Subject'] = ("(%s) Test Email @ " % status) + (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
            msg['From'] = 'help@cosol.com.au'
            msg['To'] = 'milan.vuckovecki@cosol.com.au'
            
            s = smtplib.SMTP('localhost')
            s.sendmail('help@cosol.com.au', ['milan.vuckovecki@cosol.com.au'], msg.as_string())
            s.quit()
            
            return True
        
        except:
            return False

    #LOG ENGINE
    def logs(self, input, option='a'):
        
        self.text = input
        
        if option.lower() == 'n':
            print "New Log file will be created"
            
        elif option.lower() == 'a':
            print "Log file will append"   
        else:
            print("won't do anything.")

class rsync:
    
    def __init__(self, src, dst, src_host, consistency='enabled'):
        self.source_dir = src
        self.source_host = src_host
        self.destination_dir = dst
        self.consistency_flag = consistency
        
    
    def run(self):
            
        #RSYNC COMMAND TO BE EXECUTED
        rsync_command = ("rsync -arvh --dry-run --delete-after %s %s" % (self.source_dir,self.destination_dir))
    
        #START RSYNC
        try:
            rsync_exe = subprocess.Popen([rsync_command], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = rsync_exe.communicate()
    
            if stderr: #IF ERRORS ARE FOUND
                
                #SAVE RSYNC ERROR
                self.error = stderr
                
                #RETURN FALSE BECAUSE OF AN ERROR
                return False

            elif stdout: #IF NO ERRORS ARE FOUND
                
                #SAVE OUTPUT
                self.raw_output = stdout.split('\n')
                              
                #COLLECT RSYNC OUTPUT DETAILS - Sent, Received, Speed, Size
                for line in self.raw_output:
        
                    re_sent = re.search(r'sent\s(\d+\s\w+)|sent\s(\d+.\d+\w+)', line)
                    re_received = re.search(r'received\s(\d+\s\w+)|received\s(\d+.\d+\w+)', line)
                    re_size = re.search(r'size\s\is\s(\d+\s\w+)|size\s\is\s(\d+.\d+\w+)', line)
                    re_speed = re.search(r'(\d+.\d+\w+)\sbytes/sec', line)
                    
                    if re_sent:
                        a = re.search(r'(\d+\s\w+)|(\d+.\d+\w+)', re_sent.group())
                        
                        #SAVE SENT
                        self.sent = a.group()
                    if re_received:
                        b = re.search(r'(\d+\s\w+)|(\d+.\d+\w+)', re_received.group())
                        
                        #SAVE RECEIVED
                        self.received = b.group()
                    if re_size:
                        c = re.search(r'(\d+\s\w+)|(\d+.\d+\w+)', re_size.group())
                        
                        #SAVE SIZE
                        self.size = c.group()
                    if re_speed:
                        #SAVE SPEED
                        self.speed = re_speed.group()
                        

                #GENERATE FILELIST
                self.fileList = ''
                if len(self.raw_output) == 5:
                    self.fileList = "    None - Already up to date."
                else:
                    for i in self.raw_output:
                        if re.search('/', i):
                            if re.search('\w+/sec', i):
                                pass
                            else:
                                self.fileList += ("    " + i + "\n")
                        else:
                            pass
            
                
                #OPTIONAL PARAMETER. 
                #DISABLE/ENABLE CONSISTENCY - DEFAULT: ENABLED
                if self.consistency_flag == 'enabled':
                    
                    cons = self.consistency()
                    
                    if cons:
                        #NO ERRORS
                        return True
                    else:
                        #ERRORS
                        self.rsync_error = ("There was an error calculating consistency.")
                        return False
                    
                else:             
                    #RETURN TRUE - No Consistency        
                    return True
               
        except IOError as e:#IF TOTAL FAILURE
            print e #EXIT PROGRAM       
    
    def consistency(self):
    
        try:
            #COUNT # OF SOURCE FILES
            self.consistency_src_file_count = 0
            for dirName, subdirList, fileList in os.walk(self.source_dir):
                for fname in fileList:
                    self.consistency_src_file_count += 1
            
            #COUNT # DESTINATION FILES
            self.consistency_dst_file_count = 0
            for dirName, subdirList, fileList in os.walk(self.destination_dir):
                for fname in fileList:
                    self.consistency_dst_file_count += 1
            
            #AVOID / BY 0 
            if self.consistency_dst_file_count == 0:
                self.consistency_rating = 0
            else:
                self.consistency_rating =  100 * float(self.consistency_dst_file_count) / float(self.consistency_src_file_count)
            
            #RETURN VALUES    
            return True
        
        except:
            #RETURN VALUES
            return False

class logs:
    
    def __init__(self):
        
        if os.path.isfile('log'):
            os.remove('log')
        else:
            pass
        
    def write(self, text):
        try:
            log_file = open('log', 'a')
        except IOError as e:
            print e
            
        log_file.write(text + '\n')
        print(text)
        log_file.close()

            
if __name__ == '__main__':
    
    #VARIABLES
    src = '/mnt/src/finance'
    dst = '/mnt/dst/finance'
    host = '10.3.3.29'
 
    #CLEAR SCREEN
    os.system('clear')
    
    #Initiate LOGS()
    log = logs()
    
    log.write("\nBACKUP SCRIPT V0.2")
    log.write("------------------")
    log.write("\n[+] Initializing...")
    
    #INITIALIZING ENVIRONMENT PRIOR TO BACKUP TAKING PLACE
    try:
        tools = utils(src,dst,host)
    except IOError as e:
        print e
    
    #PING TEST
    log.write("\n[+] Checking source (%s) connectivity..." % host)
    
    if tools.ping():
        log.write("[+] Host (%s) is ONLINE" % host)
        log.write("[+] Latency: %d" % tools.ping_latency)
    else:
        log.write("[!] Host (%s) is OFFLINE" % host)
        #EMAIL
        sys.exit()
        
    log.write("\n[+] Checking source mount (%s) point..." % src)
    
    #MOUNT CHECK
    if tools.mount(src):
        log.write("[+] Mount point OK.")
    else:
        log.write("[!] Mount point not found!")
        #EMAIL
        sys.exit()
    
    log.write("\n[+] Checking destination (%s) path..." % dst)
    
    #PATH CHECK
    if tools.path():
        log.write("[+] Destination path OK")
    else:
        log.write("[!] Destination path cannot be found")
        #EMAIL
        sys.exit()
        
    log.write("\n[+] Checking available disk space on (%s)..." % dst)
    
    #DISK SPACE CHECK
    if tools.space(dst):
        log.write("[+] Disk statistics: ")
        log.write("[+] Size: %s \t Available: %s" % (tools.space_size, tools.space_avail))
        log.write("[+] Used: %s \t Percent Used: %s" % (tools.space_used, tools.space_percent))        
        log.write("[+] Warnings: NONE")
    else:
        log.write("[!] Unable to gather disk statistics!")
        #EMAIL
        sys.exit()
        
    log.write("\n[+] Checking source for Crypt-Locker infections...")    
    
    #CRYPTO VIRUS CHECK
    if tools.crypto(src):
        log.write("[+] Scanned files count: %s" % tools.crypto_count_clean)
        log.write("[+] No infections detected.")
    else:
        log.write("[+] Scanned files count: %s" % tools.crypto_count_clean)
        log.write("\n[!] Infection detected!")
        log.write("[!] Number of infected files: %s" % tools.crypto_count_infected)
        log.write("[!] File location(s): \n")
        for i in tools.crypto_infected_files:
            log.write(i) 
        
        log.write("[!] Exiting script!")
        #EMAIL
        sys.exit()    
    
    #RUN RSYNC BACKUP
    try:
        rsync = rsync(src,dst,host)
    except IOError as e:
        print e
        
    #START BACKUP
    log.write("\n[+] Starting RSYNC backup from (%s) to (%s)..." % (src, dst))
    if rsync.run():
        log.write("[+] RSYNC backup completed successfully.")
        
        log.write('[+] RSYNC Statistics: ')
        log.write("[+] Sent: %s \t Received: %s" % (rsync.sent, rsync.received))
        log.write("[+] Size: %s \t Speed: %s" % (rsync.size, rsync.speed))
        
        log.write("\n[+] RSYNC Consistency: ")
        log.write("[+] Source file count: %s" % rsync.consistency_src_file_count)
        log.write("[+] Destination file count: %s" % rsync.consistency_dst_file_count)
        log.write("[+] RSYNC Consistency Rating: %s" % rsync.consistency_rating)
        
        log.write("\n[+] Fetched files: \n")
        log.write(rsync.fileList)


    else:
        log.write(rsync.error)
        #EMAIL
        sys.exit()    
        
 
        
    
    




        