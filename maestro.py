from db import *
from copaapi import *
import threading
import time
import string
import subprocess
import pkgutil
import sys

ASSINATURA_IMAGEM = '49a3367db269'

#req_api(container_pool, container_name, operation, parameters={}):

def implantar_antena(nome_antena):	
	#split 1 e 2 estavam na edge
	
	global ASSINATURA_IMAGEM
	
	print 'implantando antena ' + nome_antena
	print 'Implantando Split 1'
	#t1 = threading.Thread(name='non-daemon', target=req_api, args=["edge", nome_antena + "split1", "create", {"image_type":ASSINATURA_IMAGEM}])
	t1 = threading.Thread(name='non-daemon', target=req_api, args=["edge", nome_antena + "split1", "create", {"image_type":ASSINATURA_IMAGEM}])
	t1.start()
	
	print 'Implantando Split 2'
	#t2 = threading.Thread(name='non-daemon', target=req_api, args=["edge", nome_antena + "split2", "create", {"image_type":ASSINATURA_IMAGEM}])
	t2 = threading.Thread(name='non-daemon', target=req_api, args=["regional", nome_antena + "split2", "create", {"image_type":ASSINATURA_IMAGEM}])
	t2.start()
	
	print 'Implantando Split 3'
	t3 = threading.Thread(name='non-daemon', target=req_api, args=["central", nome_antena + "split3", "create", {"image_type":ASSINATURA_IMAGEM}])
	t3.start()
	
	print 'Implantando RX'
	t4 = threading.Thread(name='non-daemon', target=req_api, args=["central", nome_antena + "rx", "create", {"image_type":ASSINATURA_IMAGEM}])
	t4.start()
	
	print 'Implantando USRP'
	t5 = threading.Thread(name='non-daemon', target=req_api, args=["central", nome_antena + "usrp", "create", {"image_type":ASSINATURA_IMAGEM}])
	t5.start()
	
	t1.join()
	t2.join()
	t3.join()
	t4.join()
	t5.join()
	
	#inicializar containers
	
	#a = req_api("edge", nome_antena + "split1", "start")
	a = req_api("edge", nome_antena + "split1", "start")
	print a["message"]
	#a = req_api("edge", nome_antena + "split2", "start")
	a = req_api("regional", nome_antena + "split2", "start")
	print a["message"]
	a = req_api("central", nome_antena + "split3", "start")
	print a["message"]
	a = req_api("central", nome_antena + "rx", "start")
	print a["message"]
	a = req_api("central", nome_antena + "usrp", "start")
	
	time.sleep(60)

	oper = {}
	oper['cmd'] = ['dhclient', 'eth0']
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	a = req_api("regional", nome_antena + "split2", "command_execution", oper)
	a = req_api("central", nome_antena + "split3", "command_execution", oper)
	a = req_api("central", nome_antena + "rx", "command_execution", oper)
	a = req_api("central", nome_antena + "usrp", "command_execution", oper)

	time.sleep(60)
	
	#obter o ip de cada instancia
	a = req_api("edge", nome_antena + "split1", "information")
	ip_split1 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	
	a = req_api("regional", nome_antena + "split2", "information")
	ip_split2 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	
	a = req_api("central", nome_antena + "split3", "information")
	ip_split3 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	
	a = req_api("central", nome_antena + "rx", "information")
	ip_rx =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	
	a = req_api("central", nome_antena + "usrp", "information")
	ip_usrp =  a["result"]["network"]["eth0"]["addresses"][0]["address"]

	#montar string
	string_a_substituir = "@split1=" + ip_split1 +"@split2=" + ip_split2 + "@split3=" + ip_split3 + "@usrp=" + ip_usrp + "@rx=" + ip_rx
	
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('edge','split1', '" + nome_antena + "split1', '" + nome_antena + "','" + ip_split1 + "')", True)
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('regional','split2', '" + nome_antena + "split2', '" + nome_antena + "','" + ip_split2 + "')", True)
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('central','split3', '" + nome_antena + "split3', '" + nome_antena + "','" + ip_split3 + "')", True)
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('central','usrp', '" + nome_antena + "usrp', '" + nome_antena + "','" + ip_usrp + "')", True)
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('central','rx', '" + nome_antena + "rx', '" + nome_antena + "','" + ip_rx + "')", True)
	
	print string_a_substituir
	
	oper = {}
	oper['cmd'] = ['python', '/root/replace.py', '/root/fg-stuff/default', string_a_substituir]
	
	#substituir arquivo de configuracao
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	a = req_api("regional", nome_antena + "split2", "command_execution", oper)
	a = req_api("central", nome_antena + "split3", "command_execution", oper)
	a = req_api("central", nome_antena + "rx", "command_execution", oper)
	a = req_api("central", nome_antena + "usrp", "command_execution", oper)
	
	#criar interfaces tap0 no split 1 e no RX
	oper = {}
	oper['cmd'] = ['ip', 'tuntap', 'add', 'tap0', 'mode', 'tap']
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	a = req_api("central", nome_antena + "rx", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['ifconfig', 'tap0', 'up']
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	a = req_api("central", nome_antena + "rx", "command_execution", oper)

	oper = {}
	oper['cmd'] = ['ifconfig', 'tap0', '192.168.200.1']
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['ifconfig', 'tap0', '192.168.200.2']
	a = req_api("central", nome_antena + "rx", "command_execution", oper)
	
	#pegar o mac_address	
	a = req_api("edge", nome_antena + "split1", "information")
	addr_split1 =  a["result"]["network"]["tap0"]["hwaddr"]
	
	a = req_api("central", nome_antena + "rx", "information")
	addr_rx =  a["result"]["network"]["tap0"]["hwaddr"]
	
	#adicionar o mac_address no rx e no split1 (um contra o outro)
	oper = {}
	oper['cmd'] = ['arp', '-s', '192.168.200.2', addr_rx]
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['arp', '-s', '192.168.200.1', addr_split1]
	a = req_api("central", nome_antena + "rx", "command_execution", oper)
	
	#----------inicializar os arquivos
	#fazer o python path
	#oper = {}
	#oper['cmd'] = ['export', 'PYTHONPATH=/root/fg-stuff/']
	#a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	#a = req_api("regional", nome_antena + "split2", "command_execution", oper)
	#a = req_api("central", nome_antena + "split3", "command_execution", oper)
	#a = req_api("central", nome_antena + "rx", "command_execution", oper)
	#a = req_api("central", nome_antena + "usrp", "command_execution", oper)
	
	#inicializar os arquivos
	oper = {}
	oper['cmd'] = ['sh', '/root/inicializador.sh', 'split1.py']
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['sh', '/root/inicializador.sh', 'split2.py']
	a = req_api("regional", nome_antena + "split2", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['sh', '/root/inicializador.sh', 'split3.py']
	a = req_api("central", nome_antena + "split3", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['sh', '/root/inicializador.sh', 'usrp.py']
	a = req_api("central", nome_antena + "usrp", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['sh', '/root/inicializador.sh', 'rx.py']
	a = req_api("central", nome_antena + "rx", "command_execution", oper)
	
	
	#desligar o apparmor
	print 'Desligando apparmor...'
	oper = {}
	oper['cmd'] = ['/etc/init.d/apparmor', 'teardown']
	a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	a = req_api("regional", nome_antena + "split2", "command_execution", oper)
	a = req_api("central", nome_antena + "split3", "command_execution", oper)
	a = req_api("central", nome_antena + "usrp", "command_execution", oper)
	a = req_api("central", nome_antena + "rx", "command_execution", oper)

	#ip tuntap add tap0 mode tap && ifconfig tap0 up && ifconfig tap0 192.168.200.1
	#arp -s 192.168.200.1 
	#arp -s 192.168.200.2
	print 'Fim da implantacao'

def deletar_antena(nome_antena):
	p = 0
	print 'Iniciar a remocao da antena ' + nome_antena
	for row in executa_sqlite("select dc, nome from instancias where antena = '" + nome_antena + "'"):
		a = req_api(row[0], row[1], "stop")
		print a
		a = req_api(row[0], row[1], "delete")
		print a
		p = p + 1
	#time.sleep(20)
	if p > 0:
		executa_sqlite("delete from instancias where antena = '" + nome_antena + "'")
		print nome_antena + ' foi removida com sucesso!'
	else:
		print 'Nao existem instancias para serem deletadas (' + nome_antena + ')'

def coleta_flows():
	oper = {}
	#oper["cmd"] = ['ls', '-la']
	oper["cmd"] = ["nfdump", "-o", "csv", "-R", "/tmp/tsflow/", "-s", "record/bytes"]
	return req_api("", "", 'copa_host_command', oper)["result"]

def formata_flows():
	retorno = {}
	res = coleta_flows()
	linhas = res.split('\n')
	for l in linhas:
		c = l.split(',')
		if len(c) > 15:
			if c[12].isnumeric():
				origem = c[3]
				destino = c[4]
				trafego = float(c[12]) / (1024 ** 3)
				porta = c[6]
				retorno[origem] = {}
				retorno[origem][destino] = {}
				retorno[origem][destino][porta] = trafego
	return retorno
				#print c[3] + '-' + c[4] + '-' + c[6] + '-' + str(trafego)

def retorna_informacoes_hosts():
	oper = {}	
	oper['method'] = 'executa_snmp'
	oper['args'] = "'192.168.122.168'"
	edge = req_api("", "", 'copa_module_execution', oper)
	oper['args'] = "'192.168.122.169'"
	regional = req_api("", "", 'copa_module_execution', oper)
	oper['args'] = "'192.168.122.170'"
	central = req_api("", "", 'copa_module_execution', oper)
	return edge, regional, central
	
def retorna_informacoes_flows():
	return formata_flows()
	
def retorna_todos_containers():
	antenas = {}
	for row in executa_sqlite("select dc, nome, tipo, antena from instancias"):
		if (not row[0] in antenas):
			antenas[row[0]] = []
		ant = {}
		ant["nome"] = row[1]
		ant["tipo"] = row[2]
		ant["antena"] = row[3]
		antenas[row[0]].append(ant)
	return antenas

def migrar(dc_origem, nome_containter, dc_destino):
	k = 0
	cl = ''
	while k < 3: #tres tentativas
		oper = {}
		oper['cmd'] = ['/etc/init.d/apparmor', 'teardown'] #desligar o apparmor
		a = req_api(dc_origem, nome_containter, "command_execution", oper)
		a = req_api(dc_origem, nome_containter, "migrate", {"destination_pool": dc_destino})
		k += 1 #morre uma tentativa
		if int(a['code']) == 0:		
			k += 5 #se migrou ja era, volta
			executa_sqlite("update instancias set dc = '" + dc_destino + "' where dc = '" + dc_origem  + "' and nome = '" + nome_containter + "'", True)
		cl = a
	return cl

if __name__ == "__main__":		
	print 'Executando Main'
	dirname = '/home/ariel/maestro/maestroNFVO/algoritmos'
	for importer, package_name, _ in pkgutil.iter_modules([dirname]):
		full_package_name = '%s.%s' % (dirname, package_name)
		module = importer.find_module(package_name).load_module(full_package_name)	
	module.maestro_main()
	
	'''deletar_antena('antena1')
	deletar_antena('antena2')
	deletar_antena('antena3')
	deletar_antena('antena4')
	deletar_antena('antena5')
	deletar_antena('antena6')
	deletar_antena('antena7')
	deletar_antena('antena8')
	deletar_antena('antena9')
	deletar_antena('antena10')
	deletar_antena('antena11')
	deletar_antena('antena12')
	deletar_antena('antena13')
	deletar_antena('antena14')
	deletar_antena('antena15')
	deletar_antena('antena16')'''
	#nome_antena = "antena1"
	#deletar_antena("antena1")
	#formata_flows()

	#a = req_api("edge", nome_antena + "split1", "information")
	#print a
	#ip_split1 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]

	#print formata_flows()
	
	#edge, regional, central = retorna_informacoes_hosts()
	#print retorna_informacoes_flows()

	#print edge, regional, central

	'''implantar_antena("antena1")
	implantar_antena("antena2")
	implantar_antena("antena3")
	implantar_antena("antena4")
	implantar_antena("antena5")
	implantar_antena("antena6")
	implantar_antena("antena7")
	implantar_antena("antena8")
	implantar_antena("antena9")
	implantar_antena("antena10")
	implantar_antena("antena11")
	implantar_antena("antena12")
	implantar_antena("antena13")
	implantar_antena("antena14")
	implantar_antena("antena15")
	implantar_antena("antena16")'''
	#implantar_antena("antena1")
	'''implantar_antena("antena7")
	implantar_antena("antena8")
	implantar_antena("antena9")
	implantar_antena("antena10")'''

	'''deletar_antena("antena1")
	deletar_antena("antena2")
	deletar_antena("antena3")
	deletar_antena("antena4")
	deletar_antena("antena5")
	deletar_antena("antena6")
	deletar_antena("antena7")
	deletar_antena("antena8")
	deletar_antena("antena9")
	deletar_antena("antena10")
	deletar_antena("antena11")
	deletar_antena("antena12")
	deletar_antena("antena13")
	deletar_antena("antena14")
	deletar_antena("antena15")
	deletar_antena("antena16")'''
	#implantar_antena(nome_antena)
	#nome_antena = "antena2"
	#implantar_antena(nome_antena)

	#nome_antena = 'antena3'
	#a = req_api("central", nome_antena + "split3", "information")
	#print a
	#ip_split3 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	
	#a = req_api("edge", nome_antena + "split1", "information")
	#print a
	#ip_split1 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	
	#for row in executa_sqlite('select * from instancias'):
	#	print row
	#oper = {}
	#oper['cmd'] = ['sh', '/root/script.sh', 'split1.py']
	#a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	#print a
	
	'''a = req_api("central", nome_antena + "split3", "information")
	ip_split3 =  a["result"]["network"]["eth0"]["addresses"][1]["address"]
	if ip_split3.find('.') < 0:
		ip_split3 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	print ip_split3'''
	
	#oper = {}
	#oper['cmd'] = ['cd', '/root/fg-stuff/;', 'python', 'split1.py', '&']
	#a = req_api("edge", nome_antena + "split1", "command_execution", oper)
	
	#print a
	
	
	#print ip_rx
	
	#a = req_api("regional", nome_antena + "rx", "information")
	#ip_rx =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
	
	#info = req_api("Central", "caraca", "information")
	#print "Executando maestro: ", info
