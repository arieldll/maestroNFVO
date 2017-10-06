from copaapi import *
import threading
import time

ASSINATURA_IMAGEM = 'f21c575e124d'

#req_api(container_pool, container_name, operation, parameters={}):



def implantar_antena(nome_antena):	
	#split 1 e 2 estavam na edge
	
	global ASSINATURA_IMAGEM
	
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
	print a["result"]
	#a = req_api("edge", nome_antena + "split2", "start")
	a = req_api("regional", nome_antena + "split2", "start")
	print a["result"]
	a = req_api("central", nome_antena + "split3", "start")
	print a["result"]
	a = req_api("central", nome_antena + "rx", "start")
	print a["result"]
	a = req_api("central", nome_antena + "usrp", "start")
	
	time.sleep(50)
	
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

if __name__ == "__main__":		
	print 'Executando Main'
	
	nome_antena = "antena1"		
	implantar_antena(nome_antena)
	
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
