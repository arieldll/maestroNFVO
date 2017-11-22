from db import *
from copaapi import *
import threading
import time
import string
import subprocess
import pkgutil
import sys
import matplotlib.pyplot as plt
import numpy as np
import random
from collections import deque

ASSINATURA_IMAGEM = '86d2a9b674b2'

#req_api(container_pool, container_name, operation, parameters={}):

def implantar_antena(nome_antena, lista_implantacao):	
	#split 1 e 2 estavam na edge
	
	global ASSINATURA_IMAGEM
	print lista_implantacao
	threads = []
	print 'implantando antena ' + nome_antena
	for i in lista_implantacao:
		#print '.....', i, '......'		
		print 'Implantando Split ' + i["tipo"]
		#t1 = threading.Thread(name='non-daemon', target=req_api, args=["edge", nome_antena + "split1", "create", {"image_type":ASSINATURA_IMAGEM}])
		t1 = threading.Thread(name='non-daemon', target=req_api, args=[i["dc"], nome_antena + i["tipo"], "create", {"image_type":ASSINATURA_IMAGEM}])		
		threads.append(t1)
		t1.start()
		
		'''print 'Implantando Split 2'
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
		t5.start()'''
	
	for thread in threads: 	
		thread.join()
	'''t1.join()
	t2.join()
	t3.join()
	t4.join()
	t5.join()'''
	
	time.sleep(10)
	#inicializar containers
	for i in lista_implantacao:
		a = req_api(i["dc"], nome_antena + i["tipo"], "start")
		print i["tipo"] + '........'
		print a["message"]
	
	'''#a = req_api("edge", nome_antena + "split2", "start")
	a = req_api("regional", nome_antena + "split2", "start")
	print a["message"]
	a = req_api("central", nome_antena + "split3", "start")
	print a["message"]
	a = req_api("central", nome_antena + "rx", "start")
	print a["message"]
	a = req_api("central", nome_antena + "usrp", "start")'''
	
	time.sleep(60)

	oper = {}
	oper['cmd'] = ['dhclient', 'eth0']
	
	for i in lista_implantacao:
		a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
		'''a = req_api("regional", nome_antena + "split2", "command_execution", oper)
		a = req_api("central", nome_antena + "split3", "command_execution", oper)
		a = req_api("central", nome_antena + "rx", "command_execution", oper)
		a = req_api("central", nome_antena + "usrp", "command_execution", oper)'''

	time.sleep(60)
	
	#obter o ip de cada instancia
	ip_por_tipo = {}
	for i in lista_implantacao:		
		a = req_api(i["dc"], nome_antena + i["tipo"], "information")
		print a
		tipo_ip = i["tipo"]
		oresult = a["result"]["network"]["eth0"]["addresses"][0]["address"]
		ip_por_tipo[tipo_ip] =  oresult
		'''a = req_api("regional", nome_antena + "split2", "information")
		ip_split2 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
		
		a = req_api("central", nome_antena + "split3", "information")
		ip_split3 =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
		
		a = req_api("central", nome_antena + "rx", "information")
		ip_rx =  a["result"]["network"]["eth0"]["addresses"][0]["address"]
		
		a = req_api("central", nome_antena + "usrp", "information")
		ip_usrp =  a["result"]["network"]["eth0"]["addresses"][0]["address"]'''

	#montar string
	string_a_substituir = "@split1=" + ip_por_tipo["split1"] +"@split2=" + ip_por_tipo["split2"] + "@split3=" + ip_por_tipo["split3"] + "@usrp=" + ip_por_tipo["usrp"] + "@rx=" + ip_por_tipo["rx"]
	
	for i in lista_implantacao:
		ipsx = ip_por_tipo[i["tipo"]]
		executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('" + i["dc"] + "', '" + i["tipo"] + "', '" + nome_antena + i["tipo"] + "', '" + nome_antena + "','" + ipsx + "')", True)
	
	'''executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('regional','split2', '" + nome_antena + "split2', '" + nome_antena + "','" + ip_split2 + "')", True)
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('central','split3', '" + nome_antena + "split3', '" + nome_antena + "','" + ip_split3 + "')", True)
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('central','usrp', '" + nome_antena + "usrp', '" + nome_antena + "','" + ip_usrp + "')", True)
	executa_sqlite("insert into instancias(dc, tipo, nome, antena, ip) values('central','rx', '" + nome_antena + "rx', '" + nome_antena + "','" + ip_rx + "')", True)'''
	
	print string_a_substituir
	
	oper = {}
	oper['cmd'] = ['python', '/root/replace.py', '/root/fg-stuff/default', string_a_substituir]
	
	#substituir arquivo de configuracao
	for i in lista_implantacao:
		a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
		'''a = req_api("regional", nome_antena + "split2", "command_execution", oper)
		a = req_api("central", nome_antena + "split3", "command_execution", oper)
		a = req_api("central", nome_antena + "rx", "command_execution", oper)
		a = req_api("central", nome_antena + "usrp", "command_execution", oper)'''
	
	#criar interfaces tap0 no split 1 e no RX
	oper = {}
	oper['cmd'] = ['ip', 'tuntap', 'add', 'tap0', 'mode', 'tap']
	for i in lista_implantacao:
		if i["tipo"] == 'split1' or i["tipo"] == 'rx':
			a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
		#a = req_api("central", nome_antena + "rx", "command_execution", oper)
	
	oper = {}
	oper['cmd'] = ['ifconfig', 'tap0', 'up']
	for i in lista_implantacao:
		if i["tipo"] == 'split1' or i["tipo"] == 'rx':
			a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
		#a = req_api("central", nome_antena + "rx", "command_execution", oper)

	oper = {}
	oper['cmd'] = ['ifconfig', 'tap0', '192.168.200.1']
	for i in lista_implantacao:
		if i["tipo"] == 'split1':
			a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
			break
	
	oper = {}
	oper['cmd'] = ['ifconfig', 'tap0', '192.168.200.2']
	for i in lista_implantacao:
		if i["tipo"] == 'rx':
			a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
			break
	
	addr_tipo = {}
	#pegar o mac_address	
	for i in lista_implantacao:
		if i["tipo"] == 'rx' or i["tipo"] == 'split1':
			a = req_api(i["dc"], nome_antena + i["tipo"], "information")
			addr_tipo[i["tipo"]] =  a["result"]["network"]["tap0"]["hwaddr"]
	
	'''a = req_api("central", nome_antena + "rx", "information")
	addr_rx =  a["result"]["network"]["tap0"]["hwaddr"]'''
	
	#adicionar o mac_address no rx e no split1 (um contra o outro)
	oper = {}
	oper['cmd'] = ['arp', '-s', '192.168.200.2', addr_tipo['rx']]
	for i in lista_implantacao:
		if i["tipo"] == 'split1':
			a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
			break
	
	oper = {}
	oper['cmd'] = ['arp', '-s', '192.168.200.1', addr_tipo['split1']]
	for i in lista_implantacao:
		if i['tipo'] == 'rx':
			a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
			break
	
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
	for i in lista_implantacao:
		oper = {}
		oper['cmd'] = ['nohup', '/root/inicializador.sh', i["tipo"] + '.py'] #tava sh
		a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
	
	'''oper = {}
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
	a = req_api("central", nome_antena + "rx", "command_execution", oper)'''	
	
	#desligar o apparmor
	print 'Desligando apparmor...'
	oper = {}
	oper['cmd'] = ['/etc/init.d/apparmor', 'teardown']
	for i in lista_implantacao:
		a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
		'''a = req_api("regional", nome_antena + "split2", "command_execution", oper)
		a = req_api("central", nome_antena + "split3", "command_execution", oper)
		a = req_api("central", nome_antena + "usrp", "command_execution", oper)
		a = req_api("central", nome_antena + "rx", "command_execution", oper)'''

	#ip tuntap add tap0 mode tap && ifconfig tap0 up && ifconfig tap0 192.168.200.1
	#arp -s 192.168.200.1 
	#arp -s 192.168.200.2
	
	#ping -I tap0 192.168.200.2 -f > /dev/null &
	#print 'Dando permissao...'
	#oper = {}
	#oper['cmd'] = ['chmod', '+x', '/root/gera_pings.sh']
	#a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
	
	print 'Inicializando uso...'
	oper = {}
	oper['cmd'] = ['sh', '/root/gera_pings.sh', '&']
	for i in lista_implantacao:
		if i["tipo"] == 'split1':
			a = req_api(i["dc"], nome_antena + i["tipo"], "command_execution", oper)
			break
	
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
	#oper["cmd"] = ["nfdump", "-o", "csv", "-R", "/tmp/tsflow/", "-s", "record/bytes"] #acho q n esta certo
	oper["cmd"] = ["nfdump", "-o", "csv", "-R", "/tmp/tsflow/"]
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
				#trafego = float(c[12]) / (1024 ** 3)
				trafego = float(c[12]) / (1024 ** 2)
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
	tipo_split = ''
	for i in executa_sqlite("select tipo from instancias where dc = '" + dc_origem + "' and nome = '" + nome_containter + "'"):
		tipo_split = i[0]
		break
	print 'tipo de split: ', tipo_split
	print 'iniciando processo de migracao'
	while k < 3: #tres tentativas
		oper = {}
		oper['cmd'] = ['/etc/init.d/apparmor', 'teardown'] #desligar o apparmor
		a = req_api(dc_origem, nome_containter, "command_execution", oper)
		
		oper = {}
		oper['cmd'] = ['killall', '-9', 'bash'] #feito pq pode ter terminal aberto
		a = req_api(dc_origem, nome_containter, "command_execution", oper)
		
		oper = {}
		oper['cmd'] = ['killall', 'python'] #arrancar a execucao dos splits
		a = req_api(dc_origem, nome_containter, "command_execution", oper)
		
		oper = {}
		oper['cmd'] = ['killall', '-9', 'ping'] #arrancar a execucao dos splits
		a = req_api(dc_origem, nome_containter, "command_execution", oper)
		
		print 'Tentativa ' + str(k + 1)
		a = req_api(dc_origem, nome_containter, "migrate", {"destination_pool": dc_destino})
		print a['result']
		print a['message']
		print a
		k += 1 #morre uma tentativa
		if int(a['code']) == 0:		
			k += 5 #se migrou ja era, volta
			executa_sqlite("update instancias set dc = '" + dc_destino + "' where dc = '" + dc_origem  + "' and nome = '" + nome_containter + "'", True)
			oper = {}
			oper['cmd'] = ['nohup', '/root/inicializador.sh', tipo_split + '.py']
			pax = req_api(dc_destino, nome_containter, "command_execution", oper)		
			
			if tipo_split == 'split1':
				print 'tentando reiniciar o ping....'
				#	oper = {}
				#	oper['cmd'] = ['ping', '-I', 'tap0', '192.168.200.2', '-f', '&']
				#	retx = req_api(dc_destino, nome_containter, "command_execution", oper)	
				#	print retx['result']
				oper = {}
				oper['cmd'] = ['sh', '/root/gera_pings.sh']
				pax = req_api(dc_destino, nome_containter, "command_execution", oper)		
			else:
				print 'nao eh do tipo split1' + tipo_split
		cl = a
	return cl

#!/usr/bin/env python3

class RealtimePlot:
    def __init__(self, axes,  color='r', max_entries = 100):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries
               
        self.lineplot, = axes.plot([], [], color + "o-") #ro-
        self.axes.set_autoscaley_on(True)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 50):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval)

def graficos():
    
    start = time.time()	
    
    fig, axes = plt.subplots()
    display1 = RealtimePlot(axes)
    display1.animate(fig, lambda frame_index: (time.time() - start, random.random() * 100))
    
    display2 = RealtimePlot(axes)
    display2.animate(fig, lambda frame_index: (time.time() - start, random.random() * 100))
    
    display3 = RealtimePlot(axes)
    display3.animate(fig, lambda frame_index: (time.time() - start, random.random() * 100))
    #plt.show()
    #plt.close()

    fig, axes = plt.subplots()
    display1 = RealtimePlot(axes, 'r')
    display2 = RealtimePlot(axes, 'b')
    display3 = RealtimePlot(axes, 'g')
    return display1
    #while True:
    #    display1.add(time.time() - start, random.random() * 100)
    #    display2.add(time.time() - start, random.random() * 100)
    #    display3.add(time.time() - start, random.random() * 100)
        #plt.pause(0.001)

def gera_informaces_banda_entre_vms():
	ct = {}
	acumulado = 0
	orig_dest = {}
	orig_dest['edge'] = {}
	orig_dest['regional'] = {}
	orig_dest['central'] = {}
	
	orig_dest['edge']['regional'] = 0	
	orig_dest['edge']['central'] = 0	
	orig_dest['regional']['central'] = 0
	orig_dest['regional']['edge'] = 0
	orig_dest['central']['edge'] = 0
	orig_dest['central']['regional'] = 0
	
	for r in executa_sqlite("select dc, nome, tipo, antena, ip from instancias"):
		ct[r[1]] = {} 		
		ct[r[1]]['dc'] = r[0]
		ct[r[1]]['tp'] = r[2]		
		ct[r[1]]['at'] = r[3]		
		ct[r[1]]['ip'] = r[4]
	
	fxs = retorna_informacoes_flows()
	
	acc = {}
	
	for c in ct:
		tp = ct[c]['tp']
		adc = ct[c]['dc']		
		ant = ct[c]['at']
		px = '' #proximo		
		#print tp
		if tp == 'split1':
			px = 'split2'
		elif tp == 'split2':
			px = 'split3'
		elif tp == 'split3':
			px = 'usrp'
		elif tp == 'usrp':
			px = 'rx'
		elif tp == 'rx':
			px = 'split1'
		
		prox = ant + px
		#print 'atual: ' + ant + tp
		nt = ct[prox]['dc'] #proximo dc
		#print 'prox: ' + prox
		
		conta = 0
		if nt != adc:
			ip_a = ct[c]['ip']
			ip_b = ct[prox]['ip']
			
			for x in fxs:
				if x == ip_a:
					os = fxs[x]
					for ts in os:
						if ts == ip_b:
							ls = os[ts]
							for k in ls:
								conta += ls[k]
								#print ls[k]
							#print ls
					#print fxs[x]
				#print x
			##print adc, nt
			orig_dest[adc][nt] += conta
			acumulado += conta
			#print ip_a, ip_p						
			#for i in fx[ip_a][ip_p]:
			#	print i	
	
	return orig_dest, acumulado
	

if __name__ == "__main__":		
	print 'Executando Main'
	dirname = '/home/ariel/maestro/maestroNFVO/algoritmos'
	for importer, package_name, _ in pkgutil.iter_modules([dirname]):
		full_package_name = '%s.%s' % (dirname, package_name)
		module = importer.find_module(package_name).load_module(full_package_name)	
		
	#gera_informaces_banda_entre_vms()	
	module.maestro_main()
	exit()
	#deletar_antena('antena17')
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
	deletar_antena('antena16')
	exit()'''
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
	
	
	implantar = []
	config = {}
	config["dc"] = "edge"
	config["tipo"] = "split1"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "regional"
	config["tipo"] = "split2"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "central"
	config["tipo"] = "split3"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "central"
	config["tipo"] = "usrp"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "central"
	config["tipo"] = "rx"	
	implantar.append(config)
		
	implantar_antena('antena1', implantar)
	implantar_antena('antena2', implantar)
	implantar_antena('antena3', implantar)
	implantar_antena('antena4', implantar)
	implantar_antena('antena5', implantar)
	#implantar_antena('antena17', implantar)
	#implantar_antena('antena12', implantar)
	#oper = {}
	#oper['cmd'] = ['sh', '/root/gera_pings.sh', '&']
	#a = req_api('edge', 'antena5split1', "command_execution", oper)
	
	#print 'Fim da implantacao'
	#implantar_antena('antena13', implantar)
	#implantar_antena('antena14', implantar)
	#implantar_antena('antena15', implantar)
	#implantar_antena('antena16', implantar)
	#implantar_antena('antena5', implantar)
	#implantar_antena('antena6', implantar)
	#exit()
	implantar = []
	config = {}
	config["dc"] = "regional"
	config["tipo"] = "split1"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "regional"
	config["tipo"] = "split2"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "central"
	config["tipo"] = "split3"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "central"
	config["tipo"] = "usrp"	
	implantar.append(config)
	
	config = {}
	config["dc"] = "central"
	config["tipo"] = "rx"	
	implantar.append(config)
	
	implantar_antena('antena7', implantar)
	implantar_antena('antena8', implantar)
	implantar_antena('antena9', implantar)
	implantar_antena('antena10', implantar)
	implantar_antena('antena11', implantar)
	implantar_antena('antena12', implantar)
	'''implantar_antena('antena13', implantar)
	implantar_antena('antena14', implantar)
	implantar_antena('antena15', implantar)
	implantar_antena('antena16', implantar)'''
	
	#deletar_antena('antena16')
	#deletar_antena('antena12')
	#deletar_antena('antena11')
	#deletar_antena('antena10')
	#deletar_antena('antena9')
	#deletar_antena('antena8')
	#deletar_antena('antena7')
	#deletar_antena('antena6')
	#deletar_antena('antena5')
	#deletar_antena('antena4')
	#deletar_antena('antena3')
	#deletar_antena('antena2')
	#deletar_antena('antena1')
	
	#implantar_antena("antena1", implantar)
	#deletar_antena("antena5")
	
	#migrar('edge', 'antena5split1', 'regional')
	#migrar('regional', 'antena5split1', 'edge')
	#migrar('central', 'antena1rx', 'regional')
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
