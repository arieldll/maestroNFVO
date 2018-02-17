from maestro import *
import time

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
	MEM["regional"] = float(info_regional['uso_mem']) / float(info_edge['total_mem']) * 100
	MEM["central"] = float(info_central['uso_mem']) / float(info_edge['total_mem']) * 100
	rtt_total = 0
	conta = 0
	for i in range(1, 12):
		rtt_avg = retorna_parametros_container('latencia', 'central', 'antena'+str(i)+'split1')
		print rtt_avg
		rtt_total += float(rtt_avg)
		conta += 1
	print 'Media de latencia: ' + str(rtt_total / conta)
	print CPU
	print MEM
	
	time.sleep(10)
