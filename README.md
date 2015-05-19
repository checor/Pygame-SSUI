# Control de piezoelectrico #

Este proyecto, utilizando la librería de SSUI, demuestra el control de un piezoelectrico, para su futuro uso en una máquina de generación de microgotas del departamento de Ingeniería Química del Instituto Tecnológico de Celaya.

Este código se utiliza en una tarjeta Raspberry Pi, pero puede funcionar en cualquier PC. Se recomienda utilizar una distribución de Linux para facilitar la instalación de dependencias y librerías.

### Funciones ###

* Generación de 4 ondas difrentes: senoidal, cuadrada, sierra, ruido.
* Temporizador en segundos
* Configuración guardad en archivo .ini
* Multiplataforma: Windows, Linux, Mac (no probado en Mac).
* Rango de frecuencia 1 hz - 22 Khz.
* Interfaz gráfica completamente configurable mediante YAML.
* Interfaz accesible por teclado, ratón, joystick o teclado matricial de 3x4

### Liberías y dependencias utilizadas ###

* Pygame
* Librerías de Raspberry Pi
* siggen
* GNU Screen

### Licencia ###

MIT
