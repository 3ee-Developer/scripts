import logging
import json
import os
import socket
import subprocess
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import boto3
from datetime import datetime, timezone
import time

# Cargar variables desde archivo .env si existe
load_dotenv()

# Obtener el token de Slack desde variables de entorno
slack_token = os.getenv('SLACK_TOKEN')
if not slack_token:
	raise ValueError("SLACK_TOKEN no está definido en las variables de entorno. Por favor, configúralo en un archivo .env o como variable de entorno del sistema.")

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=slack_token)
logger = logging.getLogger(__name__)

# Canal de Slack para errores
slack_channel_id = "C09MCDYKG75"

# Hostname de la máquina donde se ejecuta el script
hostname = socket.gethostname()

# Path raíz del sistema (depende del hostname)
if hostname == "MacBookPro.fibertel.com.ar":
	root_path = "/Users/mconsoni/Work/3ee/scripts/sample"
else:
	root_path = "/root"

# Logs a enviar por hostname (el hostname puede ser exacto o contener la clave, ej. "ip-xxx-tasks" -> tasks)
# Completar las listas con los archivos de log de cada servidor. Rutas típicas en servidor: /root/...
LOG_FILES_BY_HOSTNAME = {
	"tasks": [
		"/root/log/apagarServerTasks.log",
		"/root/log/backoffice.log",
		"/root/log/hyperliquid_strategy.log",
		"/root/log/hyperliquid_valuation.log",
		"/root/log/shield.log",
		"/root/log/uniswap2.log",
	],
	"hyperliquid": [
		"/root/log/hyperliquid_evolution.log",
		"/root/log/apagarServerHyperliquid.log",
		"/root/defilib/logs/hyperliquid2.log",
	],
	"uniswap": [
		"/root/log/apagarServerUniswap.log",
		"/root/defilib/logs/uniswap.log",
	],
}

# Hora actual en UTC
current_datetime = datetime.now(timezone.utc)
str_current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

# ID de la instancia de la API Signer
# La unica que vamos a monitorear desde todos los servidores ya que no corre ningun script.
fireblocks_cosigner_vm = 'i-01993d9e57b195144'

# Inicializar clientes de AWS
ssm_client = boto3.client('ssm')
ec2_client = boto3.client('ec2')

# Archivo para persistir el último contenido enviado por cada archivo de log
LAST_SENT_LOGS_FILE = "last_sent_logs.json"

# Archivo para persistir la última fecha de ejecución de check_disk_space
LAST_DISK_CHECK_FILE = "last_disk_check.json"

def load_last_sent_logs():
	"""
	Carga el diccionario de últimos logs enviados desde el archivo JSON.
	"""
	try:
		if os.path.exists(LAST_SENT_LOGS_FILE):
			with open(LAST_SENT_LOGS_FILE, 'r', encoding='utf-8') as f:
				return json.load(f)
	except Exception as e:
		print(f"Error cargando last_sent_logs: {e}")
	return {}

def save_last_sent_logs(logs_dict):
	"""
	Guarda el diccionario de últimos logs enviados en el archivo JSON.
	"""
	try:
		with open(LAST_SENT_LOGS_FILE, 'w', encoding='utf-8') as f:
			json.dump(logs_dict, f, indent=2, ensure_ascii=False)
	except Exception as e:
		print(f"Error guardando last_sent_logs: {e}")

def load_last_disk_check_date():
	"""
	Carga la última fecha de ejecución de check_disk_space desde el archivo JSON.
	Retorna None si no existe el archivo o hay un error.
	"""
	try:
		if os.path.exists(LAST_DISK_CHECK_FILE):
			with open(LAST_DISK_CHECK_FILE, 'r', encoding='utf-8') as f:
				data = json.load(f)
				return data.get('last_check_date')
	except Exception as e:
		print(f"Error cargando last_disk_check: {e}")
	return None

def save_last_disk_check_date(date_str):
	"""
	Guarda la última fecha de ejecución de check_disk_space en el archivo JSON.
	"""
	try:
		with open(LAST_DISK_CHECK_FILE, 'w', encoding='utf-8') as f:
			json.dump({'last_check_date': date_str}, f, indent=2, ensure_ascii=False)
	except Exception as e:
		print(f"Error guardando last_disk_check: {e}")

# Diccionario para almacenar el último contenido enviado por cada archivo de log
last_sent_logs = load_last_sent_logs()

first_message = True
def sendSlackMsg(msg=None, blocks=None):
	global first_message
	try:
		if first_message:
			client.chat_postMessage(channel=slack_channel_id, text='divider', blocks=[ { "type": "divider", } ])
			first_message = False
		if msg is not None:
			client.chat_postMessage(channel=slack_channel_id, text=msg)
		if blocks is not None:
			client.chat_postMessage(channel=slack_channel_id, text='blocks', blocks=blocks)
	except Exception as e:
		print(f"Error: {e}")


def cosigner_running():
	instance_status = ec2_client.describe_instances(InstanceIds=[fireblocks_cosigner_vm])
	if instance_status.get('Reservations', [{}])[0].get('Instances', [{}])[0].get('State', {}).get('Name') != 'stopped':
		return True
	return False


def send_logs():
	"""
	Envía las últimas líneas de los archivos de log configurados para este hostname.
	Usa LOG_FILES_BY_HOSTNAME: si el hostname coincide exactamente o contiene la clave (tasks, hyperliquid, uniswap),
	se envían los logs de esa entrada.
	"""
	global hostname
	global str_current_datetime
	global root_path
	global last_sent_logs
	
	# Resolver lista de logs según hostname: coincidencia exacta o hostname contiene la clave
	log_files = LOG_FILES_BY_HOSTNAME.get(hostname)
	if log_files is None:
		for key in LOG_FILES_BY_HOSTNAME:
			if key in hostname:
				log_files = LOG_FILES_BY_HOSTNAME[key]
				break
	if not log_files:
		return
	
	# Sustituir /root por root_path por si se ejecuta en otro entorno (ej. local)
	resolved = []
	for p in log_files:
		resolved.append(p.replace("/root", root_path) if p.startswith("/root") else p)
	log_files = resolved
	
	try:
		for log_file in log_files:
			try:
				if os.path.exists(log_file):
					# Leer las últimas 10 líneas del archivo
					result = subprocess.run(
						f"tail -n 3 {log_file}",
						shell=True,
						capture_output=True,
						text=True,
						timeout=5
					)
					
					if result.returncode == 0:
						last_lines = result.stdout.strip()
						# Verificar si el contenido es el mismo que el último enviado
						if log_file in last_sent_logs and last_sent_logs[log_file] == last_lines:
							# El contenido es el mismo, no enviar
							continue
						
						# Actualizar el último contenido enviado
						last_sent_logs[log_file] = last_lines
						# Guardar en disco para persistir entre ejecuciones
						save_last_sent_logs(last_sent_logs)
						
						# Enviar header con el nombre del archivo
						sendSlackMsg(f"{str_current_datetime} {hostname} - Log: {log_file}")
						# Enviar las últimas líneas
						if last_lines:
							# Slack tiene un límite de ~4000 caracteres por mensaje
							# Si el contenido es muy largo, dividirlo en chunks
							max_chunk_size = 3000  # Límite conservador para incluir los backticks
							code_block_start = "```\n"
							code_block_end = "\n```"
							overhead = len(code_block_start) + len(code_block_end)
							
							if len(last_lines) + overhead <= max_chunk_size:
								# Enviar todo en un solo mensaje
								sendSlackMsg(f"{code_block_start}{last_lines}{code_block_end}")
							else:
								# Dividir en líneas y enviar en chunks
								lines = last_lines.split('\n')
								current_chunk = []
								current_size = 0
								
								for line in lines:
									line_with_newline = line + '\n'
									line_size = len(line_with_newline)
									
									# Si agregar esta línea excede el límite, enviar el chunk actual
									if current_size + line_size + overhead > max_chunk_size and current_chunk:
										chunk_content = ''.join(current_chunk).rstrip('\n')
										sendSlackMsg(f"{code_block_start}{chunk_content}{code_block_end}")
										current_chunk = [line_with_newline]
										current_size = line_size
									else:
										current_chunk.append(line_with_newline)
										current_size += line_size
								
								# Enviar el último chunk si hay contenido
								if current_chunk:
									chunk_content = ''.join(current_chunk).rstrip('\n')
									sendSlackMsg(f"{code_block_start}{chunk_content}{code_block_end}")
						else:
							sendSlackMsg("(archivo vacío)")
					else:
						sendSlackMsg(f"{str_current_datetime} {hostname} - Error leyendo {log_file}: {result.stderr}")
				#else:
				#	sendSlackMsg(f"{str_current_datetime} {hostname} - Archivo no encontrado: {log_file}")
			except Exception as e:
				sendSlackMsg(f"{str_current_datetime} {hostname} - Error procesando {log_file}: {str(e)}")
	except Exception as e:
		sendSlackMsg(f"{str_current_datetime} {hostname} - Error en send_logs: {str(e)}")
	


def check_disk_space(threshold_percent=80):
	# Obtener la fecha actual en formato YYYY-MM-DD
	current_date = current_datetime.strftime("%Y-%m-%d")
	
	# Verificar si ya se ejecutó hoy
	last_check_date = load_last_disk_check_date()
	if last_check_date == current_date:
		# Ya se ejecutó hoy, salir sin hacer nada
		return None
	
	try:
		# Ejecutar comando df -h para obtener información del disco local
		# Usando df -h / para obtener el disco raíz
		result = subprocess.run(
			"df -h / | tail -n +2 | awk '{print $1,$2,$3,$4,$5}'",
			shell=True,
			capture_output=True,
			text=True,
			timeout=10
		)
		
		if result.returncode != 0:
			print(f"Error ejecutando comando df: {result.stderr}")
			return None
		
		# Parsear el resultado: Filesystem Size Used Avail Use%
		output = result.stdout.strip()
		parts = output.split()
		if len(parts) >= 5:
			filesystem = parts[0]
			size = parts[1]
			used = parts[2]
			avail = parts[3]
			use_percent_str = parts[4].rstrip('%')
			use_percent = int(use_percent_str)
			
			disk_info = {
				'filesystem': filesystem,
				'size': size,
				'used': used,
				'avail': avail,
				'use_percent': use_percent,
				'hostname': hostname
			}
			
			# Verificar si excede el umbral
			if use_percent >= threshold_percent:
				msg = (f"{str_current_datetime} {hostname} - Uso del disco excediendo el {threshold_percent}% - "
					   f"Disco {filesystem} al {use_percent}% de capacidad "
					   f"(Usado: {used}, Disponible: {avail}, Total: {size})")
				sendSlackMsg(msg)
			
			# Guardar la fecha de ejecución exitosa
			save_last_disk_check_date(current_date)
			
			return disk_info
		else:
			print(f"No se pudo parsear el resultado del comando: {output}")
			sendSlackMsg(f"{str_current_datetime} {hostname} - "
						 f"No se pudo analizar el estado del disco: {output}")
			return None
			
	except Exception as e:
		print(f"Error verificando espacio en disco para {hostname}: {str(e)}")
		sendSlackMsg(f"{str_current_datetime} {hostname} - "
					 f"Error verificando espacio en disco: {str(e)}")
		return None


def check_after_0015():
	global hostname
	global current_datetime
	global str_current_datetime

	current_hour = current_datetime.hour
	current_minute = current_datetime.minute
	if current_hour > 0 or (current_hour == 0 and current_minute > 15):
		sendSlackMsg(f"{str_current_datetime} {hostname} Sigue prendido")
		if cosigner_running():
			sendSlackMsg(f"{str_current_datetime} Fireblocks-CoSigner sigue prendido")
		send_logs()


def main():
	# Chequear el espacio en disco
	check_disk_space(threshold_percent=80)
	# Envia mensaje de que sigue prendida despues de las 00:30 UTC
	check_after_0015()


if __name__ == "__main__":
	main()
