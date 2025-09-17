# Documentación de Orquestación Lambda + Scripts EC2

## Descripción General

Este sistema automatiza la ejecución de tareas distribuidas en varias instancias EC2 utilizando una función AWS Lambda y una serie de scripts bash. El objetivo es ejecutar procesos específicos en cada instancia, asegurando que no se repitan en el mismo día y apagando automáticamente los servidores al finalizar, optimizando así el uso de recursos en AWS.

---

## Instancias EC2 y Scripts Asociados

- **tasks_vm**
    
    ID: `i-086cd22c6d66f5cab`
    
    Script específico: `fromLambdaTasks.sh` (copiado como `/root/scripts/fromLambda.sh` en esta instancia)
    
- **hyperliquid_vm**
    
    ID: `i-09a4ecb38ca786bc5`
    
    Script específico: `fromLambdaHyperliquid.sh` (copiado como `/root/scripts/fromLambda.sh` en esta instancia)
    
- **uniswap_vm**
    
    ID: `i-042ec3e7fa3906e4b`
    
    Script específico: `fromLambdaUniswap.sh` (copiado como `/root/scripts/fromLambda.sh` en esta instancia)
    
- **api_signer_vm**
    
    ID: `i-01993d9e57b195144`
    
    No ejecuta script desde Lambda, solo se inicia y apaga según el flujo.

---

## Flujo General

1. **La función Lambda (`lambda_function.py`)** se encarga de:
    - Iniciar las instancias EC2 necesarias.
    - Esperar a que estén en estado "running".
    - Ejecutar, mediante AWS SSM, el script `/root/scripts/fromLambda.sh` en cada instancia de trabajo.
    - Esperar a que las instancias terminen su trabajo y se detengan.
    - Finalmente, apagar la instancia de firma (`api_signer_vm`).

2. **En cada instancia de trabajo**, el archivo `/root/scripts/fromLambda.sh` es una copia del script correspondiente a esa instancia:
    - En `tasks_vm`, `/root/scripts/fromLambda.sh` es una copia de `fromLambdaTasks.sh`
    - En `hyperliquid_vm`, `/root/scripts/fromLambda.sh` es una copia de `fromLambdaHyperliquid.sh`
    - En `uniswap_vm`, `/root/scripts/fromLambda.sh` es una copia de `fromLambdaUniswap.sh`
    
    Esto se realiza durante el despliegue de los scripts en cada servidor.

---

## Detalle de la Ejecución en Cada Instancia

### 1. **fromLambdaTasks.sh** (en `tasks_vm`)

- Verifica si ya se ejecutó ese día (usando un archivo de control en `/root/log/fromLambdaLastRun.log`).
- Si ya corrió, registra el evento y apaga la instancia.
- Si no corrió:
    - Actualiza el archivo de control con la fecha actual.
    - Ejecuta en segundo plano:
        - `backoffice.sh` - Ejecuta `aws_run.py` en el directorio `/root/backoffice`
        - `uniswap2.sh` - Ejecuta `valuate-and-run.py uniswap2` en `/root/defilib`
        - `hyperliquid.sh` - Ejecuta `valuate-and-run.py hyperliquid` en `/root/defilib`
        - `shield.sh` - Ejecuta `valuate-and-run.py damm` en `/root/defilib`
    - Al finalizar, ejecuta `apagarServerTasks.sh` para apagar la instancia.

### 2. **fromLambdaHyperliquid.sh** (en `hyperliquid_vm`)

- Verifica si ya se ejecutó ese día.
- Si ya corrió, registra el evento y apaga la instancia.
- Si no corrió:
    - Actualiza el archivo de control con la fecha actual.
    - Ejecuta en segundo plano:
        - `hyperliquid_evolution.sh` - Ejecuta `valuation_hyperliquid_evolution.py` en `/root/defilib`
    - Al finalizar, ejecuta `apagarServerHyperliquid.sh` para apagar la instancia.

### 3. **fromLambdaUniswap.sh** (en `uniswap_vm`)

- Verifica si ya se ejecutó ese día.
- Si ya corrió, registra el evento y apaga la instancia.
- Si no corrió:
    - Actualiza el archivo de control con la fecha actual.
    - Ejecuta en segundo plano:
        - `uniswap.sh` - Ejecuta `uni_main.py` en `/root/defilib`
    - Al finalizar, ejecuta `apagarServerUniswap.sh` para apagar la instancia.

---

## Scripts de Apagado Automático

Cada instancia tiene su script de apagado correspondiente que:

1. **Espera un tiempo inicial** (300-900 segundos según la instancia)
2. **Monitorea procesos específicos** hasta que terminen:
   - `apagarServerTasks.sh`: Monitorea `aws_run.py` y `valuate_and-run`
   - `apagarServerHyperliquid.sh`: Monitorea `valuation_hyperliquid_evolution.py`
   - `apagarServerUniswap.sh`: Monitorea `uni_main.py`
3. **Apaga la instancia** usando AWS CLI cuando los procesos terminan

---

## Scripts de Negocio

### Scripts de Backoffice
- **`backoffice.sh`**: Ejecuta `aws_run.py` en el entorno virtual de `/root/backoffice`

### Scripts de DeFi
- **`hyperliquid.sh`**: Ejecuta `valuate-and-run.py hyperliquid` en `/root/defilib`
- **`hyperliquid_evolution.sh`**: Ejecuta `valuation_hyperliquid_evolution.py` en `/root/defilib`
- **`uniswap.sh`**: Ejecuta `uni_main.py` en `/root/defilib`
- **`uniswap2.sh`**: Ejecuta `valuate-and-run.py uniswap2` en `/root/defilib`
- **`shield.sh`**: Ejecuta `valuate-and-run.py damm` en `/root/defilib`

### Scripts de Pruebas
- **`hyperliquid_test.sh`**: Script de pruebas para Hyperliquid (comentado en fromLambdaTasks.sh)
- **`test.py`**: Script de prueba simple que muestra fecha y UID del usuario

---

## Directorios Utilizados

- `/root/log` — almacena logs de ejecución
- `/root/backoffice` — scripts de backoffice con entorno virtual
- `/root/defilib` — scripts de DeFi con entorno virtual
- `/root/scripts` — scripts de orquestación y apagado

---

## Archivos de Control

- `/root/log/fromLambdaLastRun.log` — controla que cada script solo se ejecute una vez por día
- `/root/log/fromLambda.log` — log general de ejecución
- Logs específicos por script en `/root/log/` (ej: `backoffice.log`, `hyperliquid.log`, etc.)

---

## Resumen de la Relación Lambda–Scripts

- **La función Lambda** ejecuta siempre `/root/scripts/fromLambda.sh` en cada instancia de trabajo.
- **Durante el despliegue**, el contenido de `/root/scripts/fromLambda.sh` se copia desde el script específico para esa instancia (`fromLambdaTasks.sh`, `fromLambdaHyperliquid.sh` o `fromLambdaUniswap.sh`).
- **Cada script principal** se encarga de:
    - Evitar ejecuciones duplicadas en el mismo día.
    - Lanzar los procesos de negocio en background.
    - Apagar la instancia automáticamente al finalizar.

---

## Requisitos

- Las instancias EC2 deben tener instalado y configurado el agente SSM.
- Los scripts deben estar ubicados en `/root/scripts/` y ser ejecutables.
- Deben existir los directorios de logs y archivos de control en `/root/log/`.
- Durante el despliegue, asegurarse de copiar el script correcto a `/root/scripts/fromLambda.sh` en cada servidor.
- Los entornos virtuales deben estar configurados en `/root/backoffice/venv/` y `/root/defilib/venv/`.
- AWS CLI debe estar configurado para permitir el apagado de instancias.

---

## Ejemplo de Flujo Completo

1. Lambda inicia las instancias EC2.
2. Lambda ejecuta `/root/scripts/fromLambda.sh` en cada instancia de trabajo.
3. En cada instancia, `/root/scripts/fromLambda.sh` ejecuta los procesos definidos para esa máquina y apaga la instancia al finalizar.
4. Lambda espera a que todas las instancias de trabajo se detengan.
5. Lambda apaga la instancia de firma.

---

Esta integración asegura que cada instancia realice su tarea una sola vez por día y se apague automáticamente, logrando eficiencia y control en la automatización de procesos distribuidos.

---

## **Repositorios de GitHub**

- https://github.com/3ee-Developer/start-run-stop-instances
- https://github.com/3ee-Developer/scripts
