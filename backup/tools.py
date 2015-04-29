#!/usr/bin/python
import os, sys, subprocess, re
import smtplib, datetime
from time import sleep
from email.mime.text import MIMEText

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
		print('[+] Host response time: %.2f ms' % latency)		
    else:
		print("[-] Host (%s) is OFFLINE." % host)
		print ("[-] Error: " + err)
		#EMAIL ALERT
		#DECIDE TO EITHER RETRY OR QUIT...
		sys.exit()

#DST DIRECTORY CHECK FUNCTION - ENSURE LOCAL DIR EXISTS, IF NOT ATTEMPT REPAIR.
def dst_check(dst):
	try:
		if os.path.exists(dst):
			print("[+] Destination (%s) is OK." % dst)
		else:
			print("[-] Destination (%s) not found." % dst)
			print("[?] Attempting to repair (%s) destination location..." % dst)
			
			try:
				os.mkdir(dst)
				print("[+] Repair was successful. Destination (%s) is now available." % dst)
			
			except:
				print("[-] Unable to repair destination (%s). Exiting script." % src)
				#EMAIL ALERT
				sys.exit()				
	except:
		print("dst_check() function failed")
		#EMAIL ALERT
		sys.exit()

#SRC DIRECTORY CHECK FUNCTION - ENSURE MOUNT POINT EXISTS, IF NOT ATTEMPT REPAIR.
def src_check(src): 
	try:
		if os.path.ismount(src): #Check SRC for a valid mount point.
			print("[+] Mount point (%s) is OK." % src)
		else:
			print("[-] Mount point(%s) was not found." % src)
			try:
				print("[?] Attempting to repair (%s) mount point..." % src)
				os.system('mount -a')
				if os.path.ismount(src):
					print("[+] Repair was successful. Mount point (%s) is now online." % src)
				else:
					print("[-] Unable to repair mount point (%s). Exiting script." % src)
					#EMAIL ALERT
					sys.exit()				
			except:
				print("[-] Unable to repair mount point (%s). Exiting script." % src)
				#EMAIL ALERT
				sys.exit()
	except:
		print("[-] Executing mount_check() function failed!")
		#EMAIL ALERT
		sys.exit()

# CHECKS SRC DIRECTORY FOR CRYPTO-LOCKER FILES/EXTENSIONS
def crypto_check(src):

	crypto_ext = ('html', 'htm')

	for dirName, subdirList, fileList in os.walk(src):
		#print('Found directory: %s' % dirName)
		for fname in fileList:
			ext = fname.rsplit('.',1)
			ext = ext[-1]
			if ext in crypto_ext:
				print("[-] Crypto-Locker file extension has been detected!")
				print("Directory: %s" % dirName)
				print("File: %s" % fname)
				sleep(1)
				# SORT ABOVE TO LOOK FOR DECRYPT_INSTRUCTIONS FILES... 

	
def rsync(src, dst):

    #RSYNC COMMAND TO BE EXECUTED
    rsync_command = ("rsync -arvh --dry-run --delete-after %s %s" % (src, dst))

    #RUN rsync
    try:
        rsync = subprocess.Popen([rsync_command], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = rsync.communicate()

        if stdout: #IF NO ERRORS ARE FOUND
            print stdout

        if stderr: #IF ERRORS ARE FOUND
            print stderr

    except:#IF TOTAL FAILURE
        print("ERROR: RSYNC FAILED COMPLETLEY, EXITING SCRIPT!\n")
        sys.exit()




		

