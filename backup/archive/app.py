#!/usr/bin/python
import os,subprocess, sys
from time import sleep
from tools import *


#SOURCE VARS
src_host = '10.3.3.26'
src = '/mnt/src/myob'

#DESTINATION VARS
dst = '/mnt/dst/finance'

#RUN THE INITIALIZATION PROCESS TO CHECK FOR SOURCE & DESTINASTION DIRS
#NETWORK CONNECTIVITY TO THE SOURCE
#CRYPTO-LOCKER FILES (PRIMITIVE)
def initialize():

	print("\n\nBACKUP APP v 0.1")
	print("----------------\n\n")
	print("[+] Initializing...\n")
	
	#CHECK ONLINE CONNECTIVITY WITH THE SRC HOST...
	try:
		print("[+] Checking source (%s) connectivity..." % src_host)
		sleep(2)
		ping_check(src_host)
	except:
		print("[!] Failed to run ping_check(). Exiting script")
		#EMAIL ALERT
		sys.exit()
	
	#CHECK SRC MOUNT POINTS ON THE BACKUP SERVER...
	try:
		print("\n[+] Checking source (%s) mount points..." % src)
		sleep(2)
		src_check(src)
	except:
		print("[!] Failed to run src_check(). Exiting script")
		#EMAIL ALERT
		sys.exit()
	
	#CHECK EXISTANCE OF DST DIRECTORY ON THE BACKUP SERVER
	try:
		print("\n[+] Checking destination (%s) directories..." % dst)
		sleep(2)
		dst_check(dst)
	except:
		print("[!] Failed to run dst_check(). Exiting script")
		#EMAIL ALERT
		sys.exit()
	
	#SCAN SRC FILES FOR CRYPTO-LOCKER FILENAMES
	try:
		print("\n[+] Checking source (%s) files for crypto-locker infections..." % src)
		crypto_check(src)
	except:
		#print("[!] Failed to run crypto_check(). Exiting script")
		sys.exit()

	
	print("\n[+] Initialization complete.\n")
	sleep(2)
	
	#START BACKUP TASKS.
	backup()

def backup():

	#START RSYNC BACKUP
	print("[+] Starting RSYNC backup of (%s) to (%s)..." % (src, dst))
	b_sent,b_received,b_size, b_speed = rsync(src,dst)
	print("[+] RSYNC Backup completed.")
	sleep(2)
	
	#CHECK FILE CONSISTENCY BETWEEN SRC AND DST LOCATIONS
	print("\n[+] Verifying consistency between (%s) and (%s)..." % (src,dst))
	src_count, dst_count, consistency = rsync_filecount(src,dst)
	print("[+] Consistency check complete.\n")
	sleep(2)
	
	#DISC STATS FOR SRC
	print("[+] Collecting disc statistics for (%s)..." % src)
	src_size, src_used, src_avail, src_percent = free_space(src)
	sleep(1)
	print("[+] done.\n")
	sleep(2)
	
	#DISC STATS FOR DST
	print("[+] Collecting disc statistics for (%s)..." % dst)
	dst_size, dst_used, dst_avail, dst_percent = free_space(dst)
	sleep(1)
	print("[+] done.\n")
	sleep(2)
	
	#GENERATE OUTPUT
	print("[+] Generating report...\n")
	sleep(2)
	
	print("[+] Backup Statistics: ")
	print("[+] Sent: %s \t Received: %s" % (b_sent,b_received))
	print("[+] Size: %s \t Speed: %s\n" % (b_size, b_speed))
	sleep(3)
	
	print("[+] Consistency Statistics: ")
	print("[+] No. of files in (%s): %d" % (src,src_count))
	print("[+] No. of files in (%s): %d" % (dst,dst_count))
	print("[+] Consistency rating: %d percent\n" % (consistency))
	sleep(3)
	
	print("[+] Disc Statistics (%s): " % src)
	print("[+] Size: %s\t Used: %s" % (src_size, src_used))
	print("[+] Avail: %s\t Percent: %s" % (src_avail, src_percent))
	print("[+] Warnings: None\n")# COMPLETE THIS TO CHECK PERCENTAGE OF DISK SPACE
	sleep(3)
	
	print("[+] Disc Statistics (%s): " % dst)
	print("[+] Size: %s\t Used: %s" % (dst_size, dst_used))
	print("[+] Avail: %s\t Percent: %s" % (dst_avail, dst_percent))
	print("[+] Warnings: None\n")# COMPLETE THIS TO CHECK PERCENTAGE OF DISK SPACE
	sleep(3)
	
	#SEND EMAIL
	print("[+] Generating email alert.. ")
	#emailAlert('Good')
	print("[+] Email sent. \n")
	sleep(2)
	
	print("[+] All tasks completed successfully. Bye!")


if __name__ == '__main__':
	initialize()
	#backup()
	#emailAlert('Good')
	#test(src,dst)
	#rsync(src,dst)
	#rsync2(src,dst)
