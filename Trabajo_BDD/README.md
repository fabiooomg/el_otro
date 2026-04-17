# Club Social y Deportivo DCColo - E1

## 1. Análisis del problema
(texto explicando el dominio)

## 2. Modelo E/R
(imagen de tu diagrama + explicación de decisiones)

## 3. Esquema Relacional

Sintaxis: **atributo** indica llave primaria y →TABLA indica llave foránea.

### Personas:
PERSONA (**Nombre**: VARCHAR(100), correo: VARCHAR(100), direccion: VARCHAR(100), telefono: VARCHAR(100), Alternativo: VARCHAR(100), RUN: VARCHAR(100))
> REGION está en BCNF porque la única dependencia funcional es 
> cod_region → nombre, donde cod_region es llave primaria.

### Socios

### REGION
REGION (**cod_region**: INT, nombre: VARCHAR(100))
> Justificación BCNF: ...

### COMUNA
COMUNA (**cod_comuna**: INT, nombre: VARCHAR(100), cod_region→REGION: INT)
> Justificación BCNF: ...

### 

## 4. Consultas SQL
(las 5 consultas)

## 5. Referencias