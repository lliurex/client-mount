#!/usr/bin/env python

import os
import shutil
import tempfile
import threading

import n4d.server.core
import n4d.responses

class ClientPamMount:
	
	def __init__(self):
		
		self.core=n4d.server.core.Core.get_core()
		self.pam_skel="/etc/security/pam_mount.conf.xml.lliurex.skel"
		self.pam_file="/etc/security/pam_mount.conf.xml.lliurex"
		self.key="%%SERVER%%"
		
	#def init


	def startup(self,options):
		
		if options["boot"]:
			t = threading.Thread(target=self._startup)
			t.daemon = True
			t.start()
		
	#def startup


	def _startup(self):
		
		try:
			# revert to server first thing, instead of waiting for a 10times timeout
			self.set_address("server")
			# Then try to get server ip
			self.configure_xml()
			
		except Exception as e:
			print(str(e))
			
	#def _startup
	
	
	def uchmod(self,file,mode):
		
		prevmask = os.umask(0)
		os.chmod(file,mode)
		os.umask(prevmask)
		
	#def uchmod

	def set_address(self,address):
		
		if os.path.exists(self.pam_skel):
			
			f=open(self.pam_skel)
			tmp,filename=tempfile.mkstemp()
			tmp_file = open(filename,'w')
			for line in f.readlines():
				tmp_file.write(line.replace(self.key,address))
				
			f.close()
			tmp_file.close()
			self.uchmod(filename,0o644)
				
			shutil.copy(filename,self.pam_file)
			os.remove(filename)
			
			return True
			
		return False
		
	#def set_address

	
	def configure_xml(self):

		configured=False

		# Making sure we're able to read SRV_IP var from server
		tries=10
		for x in range(0,tries):
			
			ret=self.core.get_variable("SRV_IP")
			if ret["status"]==0:
				ip=ret["return"]
				if ip != None:
					if self.set_address(ip):
						configured=True
						break
				
			else:
				# lets sleep and try again
				time.sleep(1)
		
		if configured:
			return n4d.responses.build_successful_call_response(True,"pam_mount updated to server IP")
		else:
			return n4d.responses.build_successful_call_response(False,"Unable to resolve server. pam_mount fallen back to 'server'")

	#def configure_xml
	
