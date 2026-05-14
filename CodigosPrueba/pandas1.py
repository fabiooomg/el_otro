import pandas as pd

datos_peliculas = {
    'Título': ['Frozen', 'Toy Story', 'The Lion King', 'Moana', 'Coco'],
    'Año': [2013, 1995, 1994, 2016, 2017],
    'Género': ['Animación', 'Animación', 'Animación', 'Animación', 'Animación'],
    'Duración': [102, 81, 88, 107, 105],
    'Calificación': [7.4, 8.3, 8.5, 7.6, 8.4]
}

df_peliculas = pd.DataFrame(datos_peliculas)

df_peliculas