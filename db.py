import sqlite3
def init():
	global conn
	global sqlite_command
	conn = sqlite3.connect('maestro.db')
	sqlite_command = conn.cursor()

def executa_sqlite(comando, commit = False):
	global sqlite_command
	#sqlite_command.execute('CREATE TABLE IF NOT EXISTS deployment(data_center text, valor integer)')
	dardos = sqlite_command.execute(comando)
	conn.commit()
	return dardos

init()
executa_sqlite('CREATE TABLE IF NOT EXISTS conta_instancias(numero integer)')
executa_sqlite('CREATE TABLE IF NOT EXISTS instancias(dc text, tipo text, nome text, antena text, ip text)')
