#!/usr/bin/python
import os, sys, subprocess, re
import smtplib, datetime
from time import sleep
from email.mime.text import MIMEText

#EMAIL ALERT + WITH A LOG FILE INCLUDED
def emailAlert(status):
    
    msg = MIMEText('Testing email')
    
    msg['Subject'] = ("(%s) Test Email @ " % status) + (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    msg['From'] = 'help@cosol.com.au'
    msg['To'] = 'milan.vuckovecki@cosol.com.au'
    
    s = smtplib.SMTP('localhost')
    s.sendmail('help@cosol.com.au', ['milan.vuckovecki@cosol.com.au'], msg.as_string())
    s.quit()

#AIMS TO TEST ONLINE CONNECTIVITY TO SRC HOST
def ping_check(host):
    cmd = ('ping -c 3 %s' % host)
    ping = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ping.stdout.read()
    err = ping.stderr.read()

    if output:
		latency = 0
		result = output.split('\n')
		for i in result:
			match = re.search(r'time=\w+.\w+', i)
			if match:
				raw_latency = re.search(r'\d+.\d+', match.group())
				x = raw_latency.group()
				x =float(x)
				latency += x
			else:
				pass
		latency = latency / 3
		
		print("[+] Host (%s) is ONLINE." % host)
		sleep(1)
		print('[+] Host response time: %.2f ms' % latency)
		sleep(2)		
    if err:
		print("[!] Host (%s) is OFFLINE." % host)
		print ("[!] Error: " + err)
		#EMAIL ALERT
		#DECIDE TO EITHER RETRY OR QUIT...
		sys.exit()

#DST DIRECTORY CHECK FUNCTION - ENSURE LOCAL DIR EXISTS, IF NOT ATTEMPT REPAIR.
def dst_check(dst):
	try:
		if os.path.exists(dst):
			print("[+] Destination (%s) is OK." % dst)
			sleep(2)
		else:
			print("[!] Destination (%s) not found." % dst)
			sleep(1)
			print("[?] Attempting to repair (%s) destination location..." % dst)
			sleep(2)
			
			try:
				os.mkdir(dst)
				print("[+] Repair was successful. Destination (%s) is now available." % dst)
				sleep(2)
			except:
				print("[!] Unable to repair destination (%s). Exiting script." % src)
				#EMAIL ALERT
				sys.exit()				
	except:
		print("[!] dst_check() function failed!")
		#EMAIL ALERT
		sys.exit()

#SRC DIRECTORY CHECK FUNCTION - ENSURE MOUNT POINT EXISTS, IF NOT ATTEMPT REPAIR.
def src_check(src): 
	try:
		if os.path.ismount(src): #Check SRC for a valid mount point.
			print("[+] Mount point (%s) is OK." % src)
			sleep(2)
		else:
			print("[!] Mount point(%s) was not found." % src)
			sleep(1)
			try:
				print("[?] Attempting to repair (%s) mount point..." % src)
				os.system('mount -a')
				sleep(2)
				if os.path.ismount(src):
					print("[+] Repair was successful. Mount point (%s) is now online." % src)
					sleep(2)
				else:
					print("[!] Unable to repair mount point (%s). Exiting script." % src)
					#EMAIL ALERT
					sys.exit()				
			except:
				print("[!] Unable to execute mount -a. Exiting script." % src)
				#EMAIL ALERT
				sys.exit()
	except:
		print("[!] Executing mount_check() function failed!")
		#EMAIL ALERT
		sys.exit()

# CHECKS SRC DIRECTORY FOR CRYPTO-LOCKER FILES/EXTENSIONS
def crypto_check(src):

	crypto_ext = ('crypto', 'encrypted','decrypt','decrypt_instruction','_INSTRUCTION', 'cryptolocker', 'locker')

	clean = 0
	infected = 0
	
	for dirName, subdirList, fileList in os.walk(src):
		for fname in fileList:
			clean += 1
			for ext in crypto_ext:
				if re.search(ext, fname.lower()): #REWORK THIS REPORT PEICE TO BE OUT OF THIS IF STATEMENT!
					infected += 1
					print("\n[!] Possible Crypto-Locker infection detected!")
					print("[!] ------------------------------------------------")
					print("[!] Directory: %s" % dirName)
					print("[!] File: %s" % fname)
					print("[!] ------------------------------------------------")
				else:
					pass			
	if infected > 0:
		print("\n[!] Infected file(s) have been detected - no backups will take place. ")
		print("[!] No. of infected files: %d" % infected)
		print("[!] Sending email alert and exiting script!")
		sys.exit()
	else:
		print("[+] No crypto-locker infections detected.")
		sleep(1)
		print("[+] No. of scanned files: %d" % clean)
		sleep(2)

def rsync_filecount(src,dst):
    
	src_count = 0
	for dirName, subdirList, fileList in os.walk(src):
		for fname in fileList:
			src_count += 1
	
	dst_count = 0
	for dirName, subdirList, fileList in os.walk(dst):
		for fname in fileList:
			dst_count += 1
	
	if dst_count == 0:
		consistency = 0
	else:
		consistency =  100 * float(dst_count) / float(src_count)
	
	return src_count, dst_count, consistency

def free_space(location):

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
                        #print ("[!] Failed collecting size, used, avail values.")
					else:
						(size, used, avail) = items
				
				if posto:
					if len(posto) != 1:
						print ("[!] Unable to retrieve disc statistics!")
                        #print ("[!] Failed collecting percent value.")
					else:
						percent = posto[0]
			
			return size, used, avail, percent	

		if stderr:
            print("[!] Failed executing (df -h %s)!")
            print("Error Logged: \n")
			print stderr
            
	except:
		print("free_space() failed to execute.")
		
#RSYNC BACKUP
def rsync(src, dst):
	
    #RSYNC COMMAND TO BE EXECUTED
    rsync_command = ("rsync -arvh --dry-run --delete-after %s %s" % (src,dst))

    #RUN RSYNC
    try:
        rsync = subprocess.Popen([rsync_command], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = rsync.communicate()

        if stdout: #IF NO ERRORS ARE FOUND
			output = stdout.split('\n')
						
			for line in output:
				
				re_sent = re.search(r'sent\s(\d+\s\w+)|sent\s(\d+.\d+\w+)', line)
				re_received = re.search(r'received\s(\d+\s\w+)|received\s(\d+.\d+\w+)', line)
				re_size = re.search(r'size\s\is\s(\d+\s\w+)|size\s\is\s(\d+.\d+\w+)', line)
				re_speed = re.search(r'(\d+.\d+\w+)\sbytes/sec', line)
				
				if re_sent:
					a = re.search(r'(\d+\s\w+)|(\d+.\d+\w+)', re_sent.group())
					sent = a.group()
				if re_received:
					b = re.search(r'(\d+\s\w+)|(\d+.\d+\w+)', re_received.group())
					received = b.group()
				if re_size:
					c = re.search(r'(\d+\s\w+)|(\d+.\d+\w+)', re_size.group())
					size = c.group()
				if re_speed:
					speed = re_speed.group()
                    
					
			return sent, received, size, speed
			
        if stderr: #IF ERRORS ARE FOUND
            print (stderr) #PACKAGE THIS FOR EMAILING...
			#EMAIL ALERT
			#sys.exit()
			

    except:#IF TOTAL FAILURE
        print("ERROR: RSYNC FAILED COMPLETLEY, EXITING SCRIPT!\n")
        sys.exit()
		

