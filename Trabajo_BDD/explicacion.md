# Informe Entrega 1 - Bases de datos IIC2413

## Datos del Alumno
| **Apellidos**       | **Nombres**          | **Número de Alumno** |
|---------------------|----------------------|----------------------|
| Condori Tembladera | Fabio Tomas    |25663100              |


## 1. Descripción y análisis del problema
 
	Club Social y Deportivo DCColo le ha solicitado construir una aplicación que gestione
    todas las actividades que el Club realiza en beneficio de sus socios.
    El club tiene socios, los que pagan cuotas mensuales para pertenecer al club y usar sus
    instalaciones. Las actividades que pueden realizar los socios son:
    Arrendar instalaciones para practicar deportes como: básquetbol, fútbol, tenis, pádel,
    natación, atletismo, etc.
    Arrendar cabañas y departamentos que DCColo tiene en distintas ubicaciones del país.
    
    Asistir al restaurant que tiene, donde los socios pueden reservar para desayunar,
    almorzar o cenar.
    Organizar actividades en el centro de eventos, como congresos, planificaciones estratégicas
    o matrimonios.
    Todos los valores de los servicios tienen vigencia, es decir el valor tiene una fecha de
    inicio y termino.
    Además los socios pueden invitar personas externas (que no son socias) para que puedan
    asistir al club y usar sus instalaciones. Las personas que son invitadas deben estar
    registradas previamente y es verificada su identidad antes de su ingreso.
    Los asistentes a eventos o restaurant también se registran pero con datos mínimos
    Como programador Junior, se te otorga la tarea de analizar y construir el modelo entidad
    relación, el esquema relacional y desarrollar consultas SQL a partir de la información y reglas
    de negocio del Club y Social Deportivo DCColo.

## 2. Solución aplicada
    Se utilizo una jerarquia IS-A para poder modelar los distintos tipos de entidades. La entidad PERSONA modela los distintos tipos de personas posibles lo cual lo hace la entidad padre, se eligio RUN como llave primaria ya que es mas facil de distingir frente a los nombres que pueden ser mas extensos. 

	
### 2.1 Modelo Entidad Relación

	Inserta aquí el diagrama del modelo E/R "diagrama.svg" 
< Usa el formato svg para evitar la perdida de calidad.>

### 2.2 Modelo Entidad Relación normalizado
![Esquema BD](./dibujin.png)

### 2.3 Consultas SQL


## 3. Referencias y bibliografía externa
<! en cada sección indica %IA, Tecnología y Prompt