# Análisis estadístico de 1000 resultados

Se ejecutaron 1000 solicitudes sobre `generador_resultados` y se consultó `evaluador_premios`, usando el motor de Logisim 2.7.1. No se modificó `tragamonedas.circ`. Las semillas son 1, 34 y 91, en ese orden, y cada ejecución comienza con estados de simulación nuevos.

El ensayo aísla estos dos módulos: no reproduce la animación ni el bloqueo por falta de créditos. El saldo se calcula como `10 + premios acumulados - tiradas`, sin límite de 8 bits ni bloqueo en cero. El juego normal habría terminado al agotar los créditos en la tirada 20. Los valores negativos posteriores sirven únicamente para estudiar la tendencia matemática.

## Resultados

| Resultado | Cantidad | Frecuencia | Referencia ideal |
|---|---:|---:|---:|
| Tres sietes | 38 | 3,8 % | 3,70 % |
| Tres campanas | 38 | 3,8 % | 3,70 % |
| Tres rayos | 35 | 3,5 % | 3,70 % |
| Sin premio | 889 | 88,9 % | 88,89 % |
| **Cualquier victoria** | **111** | **11,1 %** | **11,11 %** |

La referencia supone tres símbolos equiprobables e independientes: hay 27 combinaciones, de las cuales tres dan premio. Es una aproximación para comparar; módulo 3 introduce un sesgo mínimo y esta corrida determinista no demuestra independencia de las semillas.

Aparecieron las 27 combinaciones. En las 3000 posiciones hubo 977 sietes (32,57 %), 1010 campanas (33,67 %) y 1013 rayos (33,77 %). Se entregaron 225 créditos de premio y se descontaron 1000: variación neta de -775, saldo matemático final -765 y pérdida media de 0,775 créditos por tirada. La referencia ideal de pérdida media es 7/9, aproximadamente 0,778.

Los resultados corresponden a esta secuencia de semillas y a sus primeras 1000 solicitudes. Las frecuencias observadas no son probabilidades exactas ni garantizan los mismos porcentajes para otras semillas o cantidades de tiradas.

## Archivos

- `resultados-1000.csv`: cada tirada, sus símbolos, premio y saldo matemático.
- `resumen-1000.json`: recuentos y huellas SHA-256 del circuito y del CSV.
- `../../img/estudio-resultados-1000.png`: gráfico de victorias y símbolos, sin la curva de saldo teórico.
- `scripts/EstudioResultados.java`: automatización con los componentes reales de Logisim.
- `scripts/analizar_resultados.py`: validación, resumen y gráfico.

## Repetir el ensayo

Desde la raíz del repositorio, en PowerShell, con un JDK disponible y el archivo de Logisim 2.7.1:

```powershell
$logisimJar = 'C:/ruta/logisim-generic-2.7.1.jar'
$studyBuild = Join-Path $env:TEMP 'arqsis-estudio'
New-Item -ItemType Directory -Force -Path $studyBuild | Out-Null
javac -cp $logisimJar -d $studyBuild docs/analisis-estadistico/scripts/EstudioResultados.java
java '-Djava.awt.headless=true' -cp "$studyBuild;$logisimJar" EstudioResultados tragamonedas.circ 1000 docs/analisis-estadistico/resultados-1000.csv
python docs/analisis-estadistico/scripts/analizar_resultados.py
```

El último paso requiere Altair y vl-convert-python en el entorno de Python (`python -m pip install altair vl-convert-python`). La automatización se ejecuta por fuera del circuito entregable; no hay que incorporar un accionamiento automático de palanca en `main`.
