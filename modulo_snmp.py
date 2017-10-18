from easysnmp import Session

def executa_snmp(ip):
	session = Session(hostname=ip, community='public', version=2)

	# You may retrieve an individual OID using an SNMP GET
	#location = session.get('sysLocation.0')

	# You may also specify the OID as a tuple (name, index)
	# Note: the index is specified as a string as it can be of other types than
	# just a regular integer
	#contact = session.get(('sysContact', '0'))

	# And of course, you may use the numeric OID too
	#description = session.get('.1.3.6.1.2.1.1.1.0')

	# Set a variable using an SNMP SET
	#session.set('sysLocation.0', 'The SNMP Lab')

	# Perform an SNMP walk
	#testes 
	#teste = session.get('.1.3.6.1.4.1.2021.11.9.0')
	#teste = session.get('.1.3.6.1.4.1.2021.11.10.0')
	#teste = session.get('.1.3.6.1.4.1.2021.10.1.3.1')
	#teste = session.get('.1.3.6.1.4.1.9.9.109.1.1.1.1.5.1')
	#teste = session.get('.1.3.6.1.4.1.2021.11.50.0')
	
	porc_proc = session.get('.1.3.6.1.4.1.2021.11.11.0') #processador ocioso porcentagem
	total_mem = session.get('.1.3.6.1.4.1.2021.4.5.0') #total de memoria 
	uso_mem = session.get('.1.3.6.1.4.1.2021.4.6.0') #ram usada
	porc_disco = session.get('1.3.6.1.4.1.2021.9.1.9.1') #porcentagem uso disco
	
	info = {}
	info["porc_proc"] = porc_proc.value
	info["total_mem"] = total_mem.value
	info["uso_mem"] = uso_mem.value
	info["porc_disco"] = porc_disco.value
	
	'''nome_interfaces = session.walk('ifName')
	entr_interfaces = session.walk('ifInOctets')
	said_interfaces = session.walk('ifOutOctets')
	
	interfaces = {}
	interfaces[ip] = {}
	interfaces[ip]["memory"] = teste
	# Each returned item can be used normally as its related type (str or int)
	# but also has several extended attributes with SNMP-specific information
	#print(entr_interfaces)
	c = 0
	for item in nome_interfaces:
		interfaces[ip][str(c)] = {}
		interfaces[ip][str(c)]["index"] = str(c)
		interfaces[ip][str(c)]["snmp-id"] = item.oid
		interfaces[ip][str(c)]["name"] = item.value
		interfaces[ip][str(c)]["pktin"] = entr_interfaces[c].value
		interfaces[ip][str(c)]["pktout"] = said_interfaces[c].value
		c += 1
	return interfaces
	'''
	return info

#dados = executa_snmp('192.168.122.169')
#print dados
