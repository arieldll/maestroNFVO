from maestro import *
import time
import math

def retorna_informacao_container(dc, container):
	return req_api(dc, container, "information")

def maestro_main():	
	print 'Iniciando algoritmo personalizado'
	repete = 0
	MEMORIA = {}
	CPU = {}
	REDE = {}
	CLOUDS = ["edge", "regional", "central"]	
	FATOR = {}
	FATOR["edge"] = 15
	FATOR["regional"] = 10
	FATOR["central"] = 6
	while True:
		print 'Maestro Orchestrator Loop'
		info_edge, info_regional, info_central = retorna_informacoes_hosts()	#minuto a minuto	
		
		info_edge = info_edge["result"]
		info_regional = info_regional["result"]
		info_central = info_central["result"]
		
		porc_proc_edge = 100 - float(info_edge["porc_proc"])
		porc_proc_regional = 100 - float(info_regional["porc_proc"])
		porc_proc_central = 100 - float(info_central["porc_proc"])
		
		CPU["edge"] = porc_proc_edge
		CPU["regional"] = porc_proc_regional
		CPU["central"] = porc_proc_central
		
		'''print float(info_edge["uso_mem"])
		print float(info_edge["total_mem"])
		print '--------------'
		print float(info_regional["uso_mem"])
		print float(info_regional["total_mem"])
		print '--------------'
		print float(info_central["uso_mem"])
		print float(info_central["total_mem"])'''
		
		porc_mem_edge = (float(info_edge["uso_mem"]) / float(info_edge["total_mem"])) * 100
		porc_mem_regional = (float(info_regional["uso_mem"]) / float(info_regional["total_mem"])) * 100
		porc_mem_central = (float(info_central["uso_mem"]) / float(info_central["total_mem"])) * 100
		
		MEMORIA["edge"] = porc_mem_edge
		MEMORIA["regional"] = porc_mem_regional
		MEMORIA["central"] = porc_mem_central
		
		porc_geral_edge = (porc_proc_edge + porc_mem_edge) / 2
		porc_geral_regional = (porc_proc_regional + porc_mem_regional) / 2
		porc_geral_central = (porc_proc_central + porc_mem_central) / 2		
		
		containers = retorna_todos_containers()		
		
		print porc_proc_edge
		print porc_proc_regional
		print porc_proc_central
		
		print retorna_informacoes_flows()
		
		cloud_mais_ocupado = ''
		for c in CLOUDS:
			disp = {}
			print '-- Analisando CLOUD ' + c + ' -- .... Livre para ' + str(math.floor((102 - CPU[c]) / FATOR[c]))
			if CPU[c] > 98:
				for s in CLOUDS:
					if s != c:
						print '>' + s + ':'
						disp[s] = math.floor((102 - CPU[s]) / FATOR[s])
						print disp[s]
				
				for s in disp:
					val = disp[s]
					if val > 0:
						mig = 0
						if c == 'central': #central esta cheio							
							if s == 'edge':
								move_de = "regional"
							if s == 'regional':
								move_de = 'central'
						if c == 'edge': #edge
							if s == 'regional':
								move_de = 'edge'
							if s == 'central':
								move_de = 'regional'								
						for k in containers[move_de]:
							if mig < disp[s]:									
								a = migrar(move_de, k["nome"], s)
								a = {}
								a['code'] = 0
								if int(a['code']) == 0:
									print 'Funcao '+ k["nome"] +'migrada da ' + move_de + ' para ' + s
									mig = mig + 1
						time.sleep(130)
						break
				else:
					print 'Nao ha recursos disponiveis para realocar'
		'''
		#sobrecarga em algum cloud
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
				if b <> 0:
					a = retorna_informacao_container('edge', c['nome'])
					if a['code'] <> 0:
						continue
					state = str(a['result']['state']).lower()
					if state == 'running':
						print 'migrar', c['nome'], move_para
						a = migrar('edge', c['nome'], move_para)
						print 'message: ', a['message']
						if int(a['code']) == 0:
							b += 1
							print 'migrou certo!!!!' + str(b)
					if b == 1:
						print 'tentou parar cu de cachorro'
						time.sleep(60)
						break
					else:
						print 'python bugado' + str(b)
					
		
		elif porc_proc_regional > 99:
			move_para = 'central'
			if porc_mem_regional > 95:
				move_para = 'redge'
			if porc_mem_edge > 95:
				print 'Sem o que fazer, todas estao cheias'
				continue	
		elif porc_proc_central > 99:
			FATOR = 15
			estado_edge = porc_proc_edge
			estado_regional = porc_proc_regional
			
			quantas_cabem_edge = (100 - estado_edge) / FATOR
			quantas_cabem_edge = math.floor(quantas_cabem_edge)
			
			quantas_cabem_regional = (100 - estado_regional) / (FATOR * 0.75)
			quantas_cabem_regional = math.floor(quantas_cabem_regional)
			
			print '>>>>>>>>>> cabem na edge: ' + str(quantas_cabem_edge)
			print '>>>>>>>>>> cabem na regional: ' + str(quantas_cabem_regional)					
			
		else:
			print ' - - Nada a fazer - - '
			print 'edge - ' + str(porc_proc_edge)
			print 'regional - ' + str(porc_proc_regional)
			print 'central - ' + str(porc_proc_central)
		#aguardar tempo'''
		time.sleep(10)
		repete += 1
