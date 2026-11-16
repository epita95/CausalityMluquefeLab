# Añadir un integrante

1. Copia uno de los archivos JSON de esta carpeta y cambia el nombre del archivo y el `slug` (solo minúsculas, números y guiones).
2. Completa `given_name` (nombres) y `family_name` (apellidos), además de `name`, `role`, `home_role`, `bio`, `appointments` y `research_areas` tanto en `es` como en `en`. `order` controla la posición en el equipo.
3. Guarda la foto sin fondo en `site/assets/people/` e indica su ruta relativa a `assets` en `photo`. Si no hay foto, deja `photo` vacío para usar la imagen provisional. `home_photo` permite indicar otra imagen para la portada; si se omite, se usa `photo`. Los perfiles muestran una base recta y la portada aplica una curva solo en la parte inferior.
4. Incluye solo los enlaces disponibles en `links` (`orcid`, `scholar`, `github`, `linkedin`, `email`); pueden quedar vacíos. Los cargos y las áreas relacionadas también son opcionales.
5. Ejecuta `quarto render` desde `site/` o `python3 scripts/build.py` desde la raíz. El perfil y su ficha en el inicio se generan automáticamente para ambos idiomas.

Las áreas disponibles son `complex-treatments`, `targeted-learning`, `conformal-inference` y `population-health`. Cada área se presenta con un gráfico y un único título y descripción, sin repetir un resumen bajo el gráfico. Con varias áreas, un selector compacto muestra la primera por defecto y permite cambiar de área. El texto de cada área se mantiene en `site/data/research-es.json` y `site/data/research-en.json`.

La sección Research de la portada se genera desde ese mismo catálogo y utiliza la misma presentación que los perfiles. Para editar sus descripciones, cambia los JSON de investigación y vuelve a renderizar.

Edita los archivos JSON para actualizar los perfiles: los archivos `site/team/.../index.qmd` y `site/es/team/.../index.qmd` se generan automáticamente y sus cambios manuales se sobrescribirán. En `bio` se admiten enlaces HTML y énfasis cuando se necesiten.
