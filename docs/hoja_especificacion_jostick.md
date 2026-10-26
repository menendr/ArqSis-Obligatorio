# Hoja de especificaciones  Joystick de Logisim

## Descripción del componente

El **Joystick**, también conocido como palanca, es un componente de entrada disponible en la biblioteca *Input/Output* de Logisim que permite simular el funcionamiento de una palanca de control.

El componente permite representar movimientos en dos direcciones: horizontal (izquierda y derecha) y vertical (arriba y abajo). Según la posición de la palanca, genera valores digitales que pueden utilizarse como entradas de otros circuitos.

## Funcionamiento y modo de uso

El joystick se representa gráficamente mediante una palanca que puede desplazarse dentro de un área delimitada.

Para utilizarlo, se debe seleccionar la herramienta *Poke Tool* de Logisim y hacer clic sobre la palanca. Manteniendo presionado el botón del mouse, es posible desplazarla en cualquier dirección.

Mientras se mueve, el componente actualiza sus salidas X e Y para representar la posición actual. Al soltar el botón del mouse, la palanca vuelve automáticamente a su posición central o de reposo.

## Entradas y salidas

El componente no posee pines de entrada, ya que su posición se controla directamente mediante la interacción del usuario.

Dispone de dos pines de salida:

| Pin | Descripción |
|---|---|
| X (superior) | Representa la posición horizontal de la palanca. |
| Y (inferior) | Representa la posición vertical de la palanca. |

Ambas salidas representan valores enteros sin signo, cuyo tamaño depende de la cantidad de bits configurada en el componente.

## Configuración

El joystick permite modificar la cantidad de bits utilizados para representar sus coordenadas mediante la propiedad *Bit Width*.
Esta configuración determina el rango de valores disponibles en cada salida. Por defecto el componente se inicializa en 4 bits, pero para nuestro uso decidimos estudiar el comportamiendo del joystick con 2 bits
Con esta configuración, los valores de salida se encuentran entre `01` y `11`, siendo `00` un valor que el componente no genera.

## 5. Valores de salida esperados

Con la configuración de 2 bits, las salidas presentan los siguientes valores según la posición de la palanca:

| Posición           | Salida X | Salida Y |
|--------------------|----------|----------|
| Centro (reposo)    | `10`     | `10`     |
| Arriba             | `10`     | `01`     |
| Abajo              | `10`     | `11`     |
| Izquierda          | `01`     | `10`     |
| Derecha            | `11`     | `10`     |
| Arriba - Izquierda | `01`     | `01`     |
| Arriba - Derecha   | `11`     | `01`     |
| Abajo - Izquierda  | `01`     | `11`     |
| Abajo - Derecha    | `11`     | `11`     |

La tabla representa las posiciones centrales y extremas de cada eje, sin considerar movimientos diagonales.

## Estado de reposo

El estado de reposo corresponde a la posición central de la palanca, a la cual regresa automáticamente cuando el usuario deja de interactuar con ella.

Con una configuración de 2 bits, ambas salidas toman el valor `10`.

Por lo tanto, el estado de reposo del componente es:

- X = `10`
- Y = `10`