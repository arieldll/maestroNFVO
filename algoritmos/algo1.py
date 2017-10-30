from maestro import *
import time

def retorna_informacao_container(dc, container):
	return req_api(dc, container, "information")

def maestro_main():
	print 'Maestro Orchestrator Loop'
	repete = 0
	while True:
		info_edge, info_regional, info_central = retorna_informacoes_hosts()		
		info_edge = info_edge["result"]
		info_regional = info_regional["result"]
		info_central = info_central["result"]
		
		porc_proc_edge = 100 - float(info_edge["porc_proc"])
		porc_proc_regional = 100 - float(info_regional["porc_proc"])
		porc_proc_central = 100 - float(info_central["porc_proc"])
		
		porc_mem_edge = float(info_edge["uso_mem"]) / float(info_edge["total_mem"]) * 100
		porc_mem_regional = float(info_regional["uso_mem"]) / float(info_regional["total_mem"]) * 100
		porc_mem_central = float(info_central["uso_mem"]) / float(info_central["total_mem"]) * 100
		
		containers = retorna_todos_containers()
		
		#sobrecarga
		if porc_proc_edge > 95:
			move_para = 'regional'
			if porc_mem_regional > 95:
				move_para = 'central'
			if porc_mem_central > 95:
				print 'Sem o que fazer, todas estao cheias'
				continue
			#selecionar os containers --
			b = 0
			for c in containers["edge"]: #vai dois aleatorios por enquanto
				a = retorna_informacao_container('edge', c['nome'])
				state = str(a['result']['state']).lower()
				if state == 'running':
					print 'migrar', c['nome'], move_para
					a = migrar('edge', c['nome'], move_para)
					print 'codigo: ', a['message']
					if int(a['code']) == 0:
						print 'codigo porr'
						b += 1
				if b >= 2:
					break
								
		else:
			print 'Nada a fazer cabron'
		#aguardar tempo
		time.sleep(10)
		repete += 1
