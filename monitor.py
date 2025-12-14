import logging
import json
import os
import socket
import subprocess
import re
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
	Busca archivos .log en {root_path}/scripts/fromLambda.sh que no estén comentados
	y envía las últimas 10 líneas de cada archivo por Slack.
	"""
	global hostname
	global str_current_datetime
	global root_path
	global last_sent_logs
	
	script_path = f"{root_path}/scripts/fromLambda.sh"
	log_files = []
	
	try:
		# Leer el archivo fromLambda.sh
		with open(script_path, 'r') as f:
			lines = f.readlines()
		
		# Primero, buscar definiciones de variables que contengan .log (ej: LOG={root_path}/log/fromLambda.log)
		variables = {}
		var_pattern = re.compile(r'^(\w+)=([^\s#]+\.log)')
		for line in lines:
			stripped_line = line.strip()
			if stripped_line.startswith('#'):
				continue
			match = var_pattern.match(stripped_line)
			if match:
				var_name = match.group(1)
				var_value = match.group(2).strip()
				variables[var_name] = var_value
		
		# Buscar líneas que contengan .log y que no estén comentadas
		# Patrón para encontrar archivos .log: >> {root_path}/log/archivo.log o >> $VARIABLE
		log_pattern = re.compile(r'>>\s+([^\s&]+)')
		
		for line in lines:
			# Saltar líneas comentadas (que empiezan con #)
			stripped_line = line.strip()
			if stripped_line.startswith('#'):
				continue
			
			# Buscar archivos .log en la línea
			matches = log_pattern.findall(line)
			for match in matches:
				log_file = match.strip()
				# Si es una variable como $LOG, expandirla
				if log_file.startswith('$'):
					var_name = log_file[1:].split('.')[0]  # Extraer nombre de variable
					if var_name in variables:
						log_file = variables[var_name]
					else:
						continue  # Variable no definida, saltar
				# Reemplazar /root con root_path en la ruta del archivo
				if '/root' in log_file:
					log_file = log_file.replace('/root', root_path)
				# Verificar que termine en .log y excluir ciertos archivos
				if log_file.endswith('.log') and log_file not in log_files:
					# Obtener solo el nombre del archivo (sin la ruta)
					file_name = os.path.basename(log_file)
					# Excluir fromLambda.log y archivos que empiecen con apagarServer
					if not log_file.endswith('fromLambda.log') and not file_name.startswith('apagarServer'):
						log_files.append(log_file)
		
		# Para cada archivo .log encontrado, leer las últimas 10 líneas
		log_files.append('/root/defilib/logs/uniswap.log')
		log_files.append('/root/defilib/logs/uniswap2.log')
		log_files.append('/root/defilib/logs/hyperliquid.log')
		log_files.append('/root/defilib/logs/hyperliquid2.log')
		log_files.append('/root/defilib/logs/damm.log')
		for log_file in log_files:
			try:
				if os.path.exists(log_file):
					# Leer las últimas 10 líneas del archivo
					result = subprocess.run(
						f"tail -n 20 {log_file}",
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
		
	except FileNotFoundError:
		sendSlackMsg(f"{str_current_datetime} {hostname} - Archivo no encontrado: {script_path}")
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
