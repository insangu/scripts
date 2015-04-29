#!/usr/bin/python
import os,subprocess, sys
from time import sleep
from tools import *

#SOURCE VARS
src_host = '10.3.3.3'
src = '/mnt/src/finance'

#DESTINATION VARS
dst = '/mnt/dst/finance/documents'

def initialize():
	#ping_check(src_host)
	#src_check(src)
	#dst_check(dst)
	#rsync(src,dst)
	crypto_check(src)

if __name__ == '__main__':
	initialize()
