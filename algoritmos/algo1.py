from maestro import *
import time

def maestro_main():
	print 'orchestration algorithm 1'
	a = 0
	while True:
		print 'Maestro Orchestator loop'
		info_edge, info_regional, info_central = retorna_informacoes_hosts()		
		proc_edge = info_edge["porc_proc"]
		proc_regional = info_regional["porc_proc"]
		proc_central = info_central["porc_proc"]
			
		#aguardar tempo
		time.sleep(5)
		a = a + 1
