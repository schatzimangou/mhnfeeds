from pymongo import MongoClient
import datetime

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.mnemosyne

def session_query(name,timespan=None):
	cursor = db.session.find(timespan)
	ips = {}
	ips_service = {}
	for document in cursor:
		try:
			source_ip = document['source_ip']
			destination_port = document['destination_port']
			
			ips[source_ip] = ips.get(source_ip, 0) + 1
			ips_service['%s, %s' %(source_ip,destination_port)] = ips_service.get('%s, %s' %(source_ip,destination_port), 0) + 1
		except:
			pass
	save_to_file('/opt/mhn/server/mhn/static/feeds/%s.txt'%name,ips,'ip, frequency')
	save_to_file('/opt/mhn/server/mhn/static/feeds/%s_service.txt'%name,ips_service,'ip, port, frequency')
	
def save_to_file(directory,feed,header):
	f = open(directory,'wb')
	f.write('%s\r\n'%header)
	for key, value in sorted(feed.iteritems(), key=lambda (k,v): (v,k), reverse=True):
		f.write('%s, %d\r\n'%(key,value))
	f.close()

now = datetime.datetime.now()
# Attackers all time by frequency of appearance and service  
session_query('ips_all')
# Attackers last 24 hours by frequency of appearance and service
session_query('ips_last_24_hours',{"timestamp": {'$gt': now - datetime.timedelta(days=1)}})
# Attackers last 7 days by frequency of appearance
session_query('ips_last_7_days',{"timestamp": {'$gt': now - datetime.timedelta(days=7)}})
# Attackers last 30 days by frequency of appearance
session_query('ips_last_30_days',{"timestamp": {'$gt': now - datetime.timedelta(days=30)}})
