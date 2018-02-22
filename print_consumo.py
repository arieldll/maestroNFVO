import time
import threading
from maestro import *

def chama_parametros(nome_antena, localizacao, vetor):	
	rtt_avg = retorna_parametros_container('latencia', localizacao, nome_antena)
	vetor[nome_antena] = rtt_avg

while True:
	info_edge, info_regional, info_central = retorna_informacoes_hosts()	#minuto a minuto	

	info_edge = info_edge["result"]
	info_regional = info_regional["result"]
	info_central = info_central["result"]

	porc_proc_edge = 100 - float(info_edge["porc_proc"])
	porc_proc_regional = 100 - float(info_regional["porc_proc"])
	porc_proc_central = 100 - float(info_central["porc_proc"])

	CPU = {}
	MEM = {}
	CPU["edge"] = porc_proc_edge
	CPU["regional"] = porc_proc_regional
	CPU["central"] = porc_proc_central

	MEM["edge"] = float(info_edge['uso_mem']) / float(info_edge['total_mem']) * 100
	MEM["regional"] = float(info_regional['uso_mem']) / float(info_regional['total_mem']) * 100
	MEM["central"] = float(info_central['uso_mem']) / float(info_central['total_mem']) * 100
	rtt_total = 0
	conta = 0
	threads = []
	resultados = {} 
	
	#print 'tentando migrar'
	#migrar('central', 'antena12split1', 'regional')
	
	containers = retorna_todos_containers()
	for dc in containers:
		for ant in containers[dc]:
			if ant['tipo'] == 'split1':
				#t1 = threading.Thread(name='non-daemon', target=req_api, args=[i["dc"], nome_antena + i["tipo"], "create", {"image_type":ASSINATURA_IMAGEM}])		
				#print 'chamando', dc, ant['nome']
				t1 = threading.Thread(name='non-daemon', target=chama_parametros, args=[ant['nome'], dc, resultados])		        
				threads.append(t1)
				t1.start()    
				t1.join()

	for thread in threads:
		thread.join()
	
	print resultados
	for i in resultados:
		rtt_avg = resultados[i]
		print rtt_avg
		rtt_total += float(rtt_avg)
		conta += 1

	print 'Media de latencia: ' + str(rtt_total / conta)
	print 'CPU'
	print CPU
	print 'Memoria'
	#print info_central['uso_mem'], info_central['total_mem']
	print MEM

	time.sleep(10)
