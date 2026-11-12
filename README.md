GRUPO: MateoJesúsJM
---------------------------------------
INTEGRANTES:
- Mateo Ruiz Rejano
- Jesús Andrés Velasco Corpas-Beltrán
- José Manuel Sayago Vega
---------------------------------------
Nuestro desarrollo se diferencia respecto a otros Arkanoids por lo siguiente:

1. Apartado visual retro: Paleta de colores diseñada para recrear la atmósfera clásica de los salones arcade.
2. Niveles de [ORIGINALES]:
  -  Ojo: Nivel con forma de ojo. Muy divertido.
  -  Laberinto: Un diseño en zigzag que aporta dinamismo.
  -  Geometry: Un pixel art sobre el popular videojuego Geometry Dash.
---------------------------------------
MODIFICACION DE arkanoid_core.py
```
# Permite ejecutar en entornos sin servidor gráfico (tests/CI).
        # CONDICIÓN AÑADIDA (os.name != "nt")
        if os.name != "nt" and "SDL_VIDEODRIVER" not in os.environ and not os.environ.get("DISPLAY"):
            os.environ["SDL_VIDEODRIVER"] = "dummy"
```
En este fragmento de inicializar_pygame() tuvimos que añadir una condición para que funcione. Sinceramente no sabemos muy bien lo que hace y hemos podido solucionarlo con ayuda de la IA.
