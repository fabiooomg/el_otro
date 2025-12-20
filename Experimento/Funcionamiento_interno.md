# Explicacion base
Tipos de cartas:
-Tropa
-Estructura
-Mixta
-IA
-Alucinaciones

Tipos de calidad:
-Comum
-Poco comun
-Raro
-Epico
-Legendario
-Hiper_cromatico

Atributos de cartas: 
-Nombre
-Vida = Vida Maxima 
-Vida Maxima -> int
-Tipo 
-Ataque -> int
    -Mult
-Defensa -> float
    -Mult
-Velocidad
-Item = None
-Precio (oro)
-Calidad

Metodos:
Atacar, Recibir daño
Presentarse!
-Si lo amerita: Habilidad 

Atributos de los Items:
-Calidad
-Magnitud
-Stat (a mejorar)
-Precio

Atributos del jugador:
-Nombre
-Cartas
-Oro
-Nivel
-Racha mas alta
-Dificultad (Facil, Normal, Dificil)

Atributos del SIS: (En archivo, se carga al iniciar)
-Cantidad de sesiones del jugador
-Nombres de cartas (Coleccion)
-Nombres de jugadores alguna vez registrados (; separated)

## Stats Tropas

### Duende:
    Vida: ★★☆☆☆
    Ataque:★★★☆☆
    Defensa: Nula
    Velocidad: ★★★★☆
    Habilidad: "Sencillo y aun asi, roto. Roba 2/3/3 de oro al atacar"
    Precio: $5

### P.E.P.P.A
    Vida: ★★★★★
    Ataque:★★★★★
    Defensa: ★★★☆☆
    Velocidad: ☆☆☆☆☆
    Habilidad: "No es un robot... creo. Cuando ataca se cura un 10/9.5/8% de su vida máxima, puede sobrecurarse hasta un 20% más de su vida máxima"
    Precio: $15

### Montapatos
    Vida: ★★★☆☆
    Ataque:★★★★☆
    Defensa: Nula
    Velocidad: ★★★★★
    Habilidad: "DUCK-RIDERRRRR! Siempre sera el primero en atacar, pero tambien el primero en ser atacado si es que no hay estructuras"
    Precio: $10

### Antimuros
    Vida: ☆☆☆☆☆
    Ataque:★★★★★ ★
    Defensa: Nula
    Velocidad: ★★★★★
    Habilidad: "El glass-canon más famoso. Buen daño, aun mejor contra estructuras (x2.0), pero morira dignamente explotado"
    Precio: $6

### Caballero-Estandarte
    Vida: ★★★★☆
    Ataque:★★☆☆☆
    Defensa: ★★★★★
    Velocidad: ★★☆☆☆
    Habilidad: "Siempre muy DETERMINADO. Su resistencia es tal que le comparte a el resto de sus compañeros un poco, algo asi como 15/17/20% de su propia armadura"
    Precio: $10

### Madre Duende
    Vida: ★★★☆☆
    Ataque:★★★☆☆
    Defensa: ★★☆☆☆
    Velocidad: ★★☆☆☆
    Habilidad: "Fan n°1 de los duendes. Transforma a las alucinaciones caidas en duendes comunes, ademas de atacar con un segundo hechizo siempre (Ataque x 0.5)"
    Precio: $13

### Skarmy
    Vida: ★★☆☆☆
    Ataque:★★★★☆
    Defensa: Nula
    Velocidad: ★★★★☆
    Habilidad: "Saben que solos no hacen nada, asi que se multiplicaron (dude.) Aun asi son demasiados inestables asi que cada vez que ataquen tendran chances de dañar con un POR 4 de su daño base sin modificadores, o morir (dude.)"
    Precio: $8

### Barbaros
    Vida: ★★★☆☆
    Ataque:★★★☆☆
    Defensa: ★★★☆☆
    Velocidad: ★★★☆☆
    Habilidad: "Problemas de ira no tratados es de las muchas cosas que estos tios tienen. Su ira solo avanzara mientras mas peleen, tambien su ataque y velocidad iran subiendo"
    Precio: $9

### Espiritu en fuego
    Vida: ★☆☆☆☆
    Ataque:★★★☆☆
    Defensa: Nula
    Velocidad: ★★★☆☆
    Habilidad: "Chiquitita pero peligrosa. Tiene cierta probabilidad de pasar desapercibido cuando lo atacan, algo asi como un 40/35/30%"
    Precio: $4

### Bombastico
    Vida: ★★★☆☆
    Ataque:★★★★☆
    Defensa: ★★☆☆☆
    Velocidad: ★★☆☆☆
    Habilidad: "Enfocao, solo ataca estructuras y cuando muere explota, dañando a todos sobre todo a la IA (x 1.3)"
    Precio: $8
 
### Angel luchona
    Vida: ★★★★☆
    Ataque:★★☆☆☆
    Defensa: ★★★☆☆
    Velocidad: ★★☆☆☆
    Habilidad: "Divina y sublime. Se encarga de que tu equipo no la manquee, asi que los cura un porcentaje de SU vida maxima cada que ataca a alguien. 20/17,5/15%"
    Precio: $14

### Larry (Por lapida only)
    Vida: ☆☆☆☆☆
    Ataque:★☆☆☆☆
    Defensa: Nula
    Velocidad: ★★★☆☆
    Habilidad: "Tal como su nombre, tiene una corta vida, un corto daño, una corta espada pero un MUY largo potencial. Puede esquivar ataques"
    Precio: $X 

## Stats Estructuras
    Poseen más vida en general que las tropas!

### Cannon
    Vida: ★★★★☆
    Ataque:★☆☆☆☆
    Defensa: ★★★★☆
    Velocidad: ★☆☆☆☆
    Habilidad: "El principal bastion de la guerra. Desarma en 50/40/30% la defensa de su enemigo"
    Precio: $7

### Tesla-T
    Vida: ★★☆☆☆
    Ataque:★★★☆☆
    Defensa: ★☆☆☆☆
    Velocidad: ★★★★☆
    Habilidad: "No esta siempre de humor, sobre todo cuando le quitan la chispa. Si ataca primero, puede electrocutar al enemigo, impidiendo que ataque en ese turno"
    Precio: $9

### Recolector de aguita
    Vida: ★★★★★ ★
    Ataque: None
    Defensa: ★★☆☆☆
    Velocidad: None
    Habilidad: "La fuente de la vida. Un pequeño tanque, que lo unico que busca es llenar la coleccion de clones. Cada 2/3/3 turnos agregara una copia de una carta en juego, en la coleccion."
    Precio: $6

### Microondas
    Vida: ★★☆☆☆
    Ataque: None
    Defensa: ★★★★☆
    Velocidad: None
    Habilidad: "Mientras mas lo dejas, mas se sobrecalienta. Acumula espiritus en fuego por turnos, +1 cada 2 turnos hasta un maximo de 6 turnos, si llega a los 6 explota y al morir libera a todos los espiritus que haya acumulado"
    Precio: $9

### Lapida
    Vida: ★★★☆☆
    Ataque:None
    Defensa: ★★★★☆
    Velocidad: ★★☆☆☆
    Habilidad: "La puerta al peor mundo, invoca al peor mal conocido cada 1/2/2 turnos"
    Precio: $11

### Bar
    Vida: ★★★☆☆
    Ataque: None
    Defensa: ★★★★☆
    Velocidad: None
    Habilidad: "Dentro se celebra la mejor fiesta del siglo, arruinalo y enfrentate a sus huespedes no tan sobrios"
    Precio: $10

### Torre Bomba
    Vida: ★★★☆☆
    Ataque:★★☆☆☆
    Defensa: ★★☆☆☆
    Velocidad: ★★★☆☆
    Habilidad: "Deja una sorpresista cuando la destruyes upsi"
    Precio: $7

### Cuartel de duendes
    Vida: ★★☆☆☆
    Ataque: None
    Defensa: ★★★☆☆
    Velocidad: None
    Habilidad: "Dentro de este cuartel, descansan los seres más malvados del planeta, no significa que sean peligrosos, solo malvados. Libera a un duende cuando es destruido y cada 3 turnos"
    Precio: $8

### INFERNO
    Vida: ★★★★☆
    Ataque:★★★☆☆
    Defensa: ★★★☆☆
    Velocidad: ★★★☆☆
    Habilidad: "El diablo se aburrio y nos dio su lampara. Es una torre capaz de quemar a todo y a todos. Se adapta a su objetivo de a poco, aumentando su daño en cada turno"
    Precio $17

## Stats IA
    #Crean Esbirros por rondas, y al destrozar a todos sus esbirros aparecen ellos, como una especie de Jefes, derrotarlos es la win-condition
    #No poseen la misma valoracion de stats que el resto de cartas, ya que de por si son mas fuertes que una carta promedio.

### CatGpt
    Vida: ꩜꩜꩜꩜
    Ataque: ꩜꩜꩜
    Defensa: ꩜꩜꩜꩜
    Velocidad: ꩜꩜
    Ultimate: "CatGPT, la IA líder de DCCatástrofe, es un experto en manipulación y chantaje. Su habilidad especial es crear una conexión emocional artificial con tu mazo, lo cual provoca que los multiplicadores de ataque y defensa de tus cartas activas se reduzcan en un 35%."

### Cowpilot
    Vida: ꩜꩜꩜꩜
    Ataque: ꩜꩜
    Defensa: ꩜꩜꩜꩜꩜
    Velocidad: ꩜
    Ultimate: "CowPilot es un experto en copiar y plagiar código sin citar. Su habilidad especial es robar el código de tu propia tarea por medio de reemplazar dos cartas aleatorias de tu mazo activo por copias idénticas de otra diferente (y como resultado, teniendo tres instancias idénticas de una misma carta en tu mazo)."

### Crok
    Vida: ꩜꩜
    Ataque: ꩜꩜꩜꩜
    Defensa: ꩜
    Velocidad: ꩜꩜꩜꩜꩜
    Ultimate: "Crok es un experto en dividir políticamente (sobre debates de computación) a tu mazo. Su habilidad especial es hacerlas cuestionar si Python realmente es el mejor lenguaje para Programación Avanzada. Esto provoca que dos cartas aleatorias se rebelen y no ataquen ni defiendan por 3 rondas."

### DeepSheep
    Vida: ꩜꩜꩜
    Ataque: ꩜꩜꩜꩜
    Defensa: ꩜꩜
    Velocidad: ꩜꩜꩜꩜
    Ultimate: "DeepSheep es un experto en la censura de información. Su habilidad especial son campañas de propaganda, donde en el menú de tu tarea, todas las cartas falsamente muestran la misma cantidad de vida disponible, ademas bloquea la informacion que tenemos de el espiar a nuestros enemigos, haciendolo impredecible, incluyendo cuando aparecera este jefe."

### Gemibee
    Vida: ꩜꩜꩜
    Ataque: ꩜꩜꩜
    Defensa: ꩜꩜꩜
    Velocidad: ꩜꩜꩜
    Ultimate: "Gemibee es la IA más analítica de DCCatástrofe, ya que tiene acceso incontrolable e ilimitado a Goosegle, un buscador de internet avanzado. Su habilidad especial es hacer uso de ella, encontrando las tácticas más frescas de combate y los datos más actualizados de tus cartas, lo que aumenta permanentemente sus multiplicadores de ataque y defensa en +5% cada vez que hace uso de su habilidad. Estos aumentos son infinitamente acumulables (es decir, hacer uso de su habilidad 30 veces significa un aumento de +150% respecto al estado inicial). cada +50% de aumentos, aumentara ademas su velocidad en +20%"

### DA-bubble
    Cuando es invocado toda la arena cambia, es desbloqueable su modo de juego "La burbuja", y todo lo que habia antes de el muere y la ronda actual termina para empezar las rondas con DA-bubble
    Vida: ꩜꩜꩜꩜꩜
    Ataque: ꩜꩜꩜꩜꩜
    Defensa: ꩜꩜꩜꩜꩜
    Velocidad: ꩜꩜꩜꩜꩜
    Ultimate: "La pesadilla final del futuro, romper la burbuja de la IA, una que refleja todas las maldades de la tecnologia, posee la fuerza de todas las IAS que la conforman y es capaz de romper el flujo del espacio-tiempo digital"
        Bonus: Aunque su pelea empieza en cierta ronda X sin esbirros, la ronda puede acabar en medio de la pelea y eso nos llevara al mismo ciclo de esbirros-jefe, bajandole la vida a DA-bubble con el paso del tiempo. Esto convierte la pelea en una de 3 fases que se activan al 100% / 70% y 40% respectivamente.

## Esbirros

### --Range 1 --

#### Grifo
    Vida: ☻
    Ataque: ☻☻
    Defensa: ☻
    Velocidad: ☻☻☻
    Habilidad: "El eslabon más abajo de la cadena, su gran gracia es ser muchas cosas a la vez, incluso si no es buena en ninguna"
    Reward: $1

#### Grifo Gigante
    Vida: ☻☻☻
    Ataque: ☻☻☻
    Defensa: ☻☻☻
    Velocidad: ☻☻
    Habilidad: "Se comio todos sus vegetales, un par de pixeles y crecio bastante más que el resto de sus co-especimenes, alienta a sus compañeros a ser más grandes, y les aumenta la vida en un 12%"
    Reward: $3

#### Vampiros
    Vida: ☻☻☻☻
    Ataque: ☻
    Defensa: ☻☻
    Velocidad: ☻☻
    Habilidad: "Amantes de noche y de la pasion, se curaran toda la sangre que sean capaces de robar, cada que lo hacem se adaptan a la velocidad de sus victimas, por lo que le copian la velocidad."
    Reward: $4

### --Range 2-- ###

#### Lagger
    Vida: ☻☻
    Ataque: ☻☻☻
    Defensa: ☻☻
    Velocidad: ☻
    Habilidad: "☺✌☺✌☺✌☺✌ ✌☟⚐☼✌ ❄☜☠ ☹✌☝✏✏✏✏ 💣✌☹👎✋❄⚐ 💣⚐☠⚐"
    Reward: $2

#### Cambia-formas
    Vida: ☻☻☻
    Ataque: ☻☻☻
    Defensa: ☻
    Velocidad: ☻☻☻
    Habilidad: "No tiene buen autoestima, aun asi no logra replicar los stats de alguien más, solo su habilidad"
    Reward: $3

#### Dark Spider-Web
    Vida: ☻☻☻☻
    Ataque: ☻☻☻
    Defensa: ☻☻
    Velocidad: ☻☻☻☻
    Habilidad: "Te atrapa en una turbia y de dudosa prosedencia teleraña si es que te atrapa, lo cual pasa si te ataca primero, lo que inhabilita a su victima, aparte le roba un par de monedas"
    Reward: $1 + 50% de lo robado

### -- Structures -- ###

#### La Cupula
    Vida: ☻☻☻☻☻ ☻
    Ataque: Nulo
    Defensa: ☻☻☻
    Velocidad: Nula
    Habilidad: "Che-pibes nos juntamos en la cupula che"
    Reward: $2

#### El Coliseo
    Vida: ☻☻☻
    Ataque: Nulo
    Defensa: ☻☻☻☻☻
    Velocidad: Nula
    Habilidad: "EL LUGAR DE LOS BELICOS Y DE LOS VERDADEROS HEROES. Genera DETERMINACION en los esbirros cercanos lo que los incita a ser 40% MÁS veloces y golpear 20% MÁS fuerte"
    Reward: $5

#### Servidor
    Vida: ☻☻☻☻
    Ataque: ☻☻☻
    Defensa: ☻☻☻
    Velocidad: ☻☻☻☻
    Habilidad: "Se conecta al internet, y trae a la vida a ciertas formas molestas de vida en forma de odio, tambien te manda ciertos virus. El internet no es tan seguro asi que quizas trae a enemigos no tan familiares, ni tan lindos, ni tan seguros...."
    Reward: $8

### --Dark Range-- ###
    Invocados por el Servidor con un spawn rate de 3% cada uno, más adelante pueden tambien ser invocados por DA-bubble solo que ahi Mariposa no lo re-invocara

#### Mariposa
    Vida: ☻
    Ataque: None
    Defensa: ☻
    Velocidad: ☻
    Habilidad:"Has escuchado acerca del efecto mariposa antes??" 
        Bonus: (Puede condenar tropas a morir, puede robarse 70-100% del dinero, puede robarse todos los items, puede invocar a DA-bubble)
    Reward: $0

#### Voyager
    Vida: ☻☻☻☻
    Ataque: ☻☻☻☻
    Defensa: ☻☻☻☻
    Velocidad: ☻☻☻☻
    Habilidad: "Encierra en una zona a todas las tropas, lo que secretamente le da el 5% de los stats de cada una de las tropas que estan ahi, siendo considerado una amenaza hiper-digital fue encerrado en los confines de la darkweb"
    Reward: $x1.5

#### MEGA-Knight
    Vida: ☻☻☻☻☻ ☻
    Ataque: ☻☻☻☻☻ ☻
    Defensa: ☻☻☻☻☻ ☻
    Velocidad: ☻☻☻
    Coolness: ☻☻☻☻☻ ☻
    Armadura: ☻☻☻☻☻ ☻
    Peso: ☻☻☻☻☻ ☻
    Amigos: ☻☻☻☻☻ ☻
    Novia: Nulo
    Gusto musical: ☻☻☻☻☻ ☻
    Press banca: ☻☻☻☻☻ ☻
    Auto: ☻☻☻☻☻ ☻
    Lenguajes de programacion que sabe: ☻☻☻
    Felicidad: ☻☻
    Euphoria: ☻☻☻☻☻ ☻☻☻☻☻ ☻☻☻☻☻ ☻☻☻☻☻
    Habilidad: "Es un pajaro? Es un avion? No! Es el ser más desbalanceado jamas creado!!!"



## ITEMS
Pueden ser portados por tropas y algunos por estructuras, aumentan las estadisticas

### Stats items - Solo para tropas
    -Anillo de vida (+10% de vida)
    -Collar de prosperidad (+25% de vida)
    -Cuchilla (+10% de ataque)
    -Espadon (+25% de ataque)
    -Escudito (+10% de armadura)
    -Peto-coraza (+25% de armadura)
    -Calcetines (+15%)
    -Las-Gloriosas (+30%)
    
### Parches - Todos las cartas aliadas
    -Ojo del vampiro (+17% de vida)
    -Calibrante (+17% de ataque)
    -Mallas de acero (+17% de armadura)

    -Capa Glitcheada (+15% de vida y armadura)
    -Piedra filosofal (+15% de armadura y ataque)
    -Polvo de python (Habilidad potenciada)
    -Parche de la codicia (+50% de oro obtenido) 
    -Escudo Deltarune (+20% en todo)

### Consumibles (Posibles de ocupar en la tienda o en la coleccion)
    -Manzana comun (Curacion de 25%)
    -Paracetamol (Curacion de 75%)
    -Vitamina Z (+50% de armadura en la siguiente ronda)
    -Inyeccion del golem (+30% de armadura en las siguientes 3 rondas)
    -Pildora Roja (+35% de ataque en la siguiente ronda)
    -Determinacion (+30% de ataque hasta el proximo jefe)
    -Pasta base (+26.67676767% de velocidad en las siguientes 3 rondas)
    -Pastel con MUCHA azucar (+45% de velocidad hasta que alguien lo sobrepase (y se coma el pastel))
    -Sopa misteriosa (esto NO puede ser bueno)
        Bonus: Puede obtener todos los buffs mencionados, por separado o a la vez, veneno, maldicion, debilidad o simplemente puede estar rica ñami ☻

