# 2D Light & Shadow Simulator (LightRaycasting)

Simulador interactivo en 2D de propagación de luz y sombras en tiempo real, desarrollado con **Python** y **Pygame**. 

Este proyecto utiliza un algoritmo de **Raycasting geométrico basado en vértices** para generar sombras dinámicas perfectas y nítidas de manera ultra-eficiente.

---

## Características Principales

* **Raycasting por Vértices (Optimizado):** Calcula colisiones directamente hacia las esquinas de los obstáculos y añade pequeños offsets diferenciales para permitir que la luz pase de largo, creando sombras geométricas exactas sin fugas.
* **Iluminación Suave (Glow Radial):** Simula la atenuación cuadrática real de la luz mediante degradados de transparencia concéntricos.
* **Mezcla Aditiva de Colores:** Los haces de luz de múltiples fuentes se fusionan físicamente usando modos de mezcla de Pygame (ej. mezclar luz cyan y naranja genera tonos blancos/rosados).
* **Faro Central (Lighthouse):** Una fuente de luz giratoria estática situada en el centro para dar dinamismo a la escena.
* **Editor de Escenarios en Tiempo Real:** Crea, arrastra extremos y elimina obstáculos sin pausar la simulación.
* **Panel de Control (HUD):** Muestra métricas de rendimiento en vivo (FPS, cantidad de rayos trazados, recuento de paredes) y una leyenda completa de los controles.

---

## Requisitos e Instalación

Este proyecto utiliza **`uv`**, un gestor de paquetes de Python extremadamente rápido.

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/jassirsalas/LightRaycasting.git
   cd LightRaycasting
   ```

2. **Instalar dependencias y ejecutar:**
   Puedes usar `uv` para instalar dependencias y ejecutar la aplicación en un solo paso:
   ```bash
   uv run python light_raycasting.py
   ```
   *(Nota: `uv` creará un entorno virtual aislado `.venv/` e instalará `pygame` de forma automática).*

---

## Controles e Interacción

| Acción | Control |
|---|---|
| **Dibujar una pared** | Clic Izquierdo y arrastrar en cualquier zona vacía. |
| **Rediseñar una pared** | Clic Izquierdo y arrastrar sobre cualquiera de sus extremos (brillan al pasar el ratón). |
| **Borrar una pared** | Clic Derecho sobre cualquiera de sus extremos. |
| **Rotar linterna** | Usar la **Rueda del ratón** (Scroll Up / Scroll Down) cuando la linterna esté activa. |
| **Cambiar color de luz** | Presionar la tecla `[C]` para ciclar entre colores neón. |
| **Modo luz del ratón** | Presionar la tecla `[M]` para alternar entre *Omnidireccional* ($360^\circ$) y *Linterna* ($60^\circ$). |
| **Alternar Faro Central** | Presionar la tecla `[L]` para encender o apagar la luz del faro giratorio. |
| **Resetear escenario** | Presionar la tecla `[R]` para eliminar todas las paredes personalizadas (excepto bordes). |
| **Renderizado visual** | Presionar la tecla `[G]` para alternar entre *Glow Suave* (degradados) e *Hilos Wireframe* (rayos de luz individuales). |

---

## Optimizaciones de Rendimiento

* **Eliminación de NumPy en el bucle principal:** Se migraron los cálculos trigonométricos individuales a la librería estándar `math` de Python, eliminando el overhead que tiene NumPy al procesar escalares uno por uno.
* **Trazado Selectivo:** En lugar de emitir cientos de rayos en todas las direcciones ciegas, solo se emiten rayos hacia los vértices presentes en la escena más unos pocos ángulos fijos de apoyo, reduciendo el cálculo matemático de colisiones drásticamente.
