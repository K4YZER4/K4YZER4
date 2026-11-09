# Guía de uso

## Qué estás publicando
Este es el repositorio del perfil, no el código fuente de tus aplicaciones. Las fichas describen los proyectos y enlazarán a sus repositorios reales. Hay dos fichas ya creadas, pero conservan campos pendientes y no afirman que todas las funcionalidades estén terminadas.

## Publicar desde GitHub
1. Crea un repositorio público cuyo nombre coincida exactamente con tu usuario de GitHub, no necesariamente con tu nombre personal.
2. Descomprime el ZIP en tu computadora.
3. En el repositorio, usa Add file → Upload files. Arrastra los ARCHIVOS Y CARPETAS del paquete, no el ZIP ni una carpeta contenedora adicional. README.md y assets deben quedar directamente en la raíz.
4. Guarda con Commit changes y abre tu perfil.
5. Si ya existe un README, guarda una copia antes de sustituirlo.
6. Para editar después, abre el archivo correspondiente, pulsa Edit y guarda otro commit.

## Publicar con Git (alternativa)
Crea el repositorio vacío primero. Abre una terminal en la carpeta descomprimida que contiene README.md. Sustituye TU_USUARIO:

    git init
    git add .
    git commit -m "Add editorial profile and project pages"
    git branch -M main
    git remote add origin https://github.com/TU_USUARIO/TU_USUARIO.git
    git push -u origin main

Esto presupone un remoto vacío y autenticación de Git ya configurada. Si ya tiene commits, clónalo primero y copia los archivos dentro; no fuerces el push.

## Qué editar
- README.md: presentación, stack y tarjetas de proyectos.
- assets/foto.png: sustituye este marcador por tu fotografía. Si usas foto.jpg, cambia la ruta en README.md.
- proyectos/restaurant-management/README.md: ficha del restaurante.
- proyectos/fitness-platform/README.md: ficha de fitness.
- proyectos/*/assets/captura.png: captura real o diagrama. No publiques información personal, tokens ni datos de clientes.
- Elimina instrucciones entre corchetes cuando completes cada sección. Puedes publicar mientras están en desarrollo, pero indica el estado y elimina lo que no quieras mostrar.
- Convierte Código, Demo y API en enlaces solo cuando tengas URLs reales.
- Conserva Jest y las demás herramientas solo si las has utilizado y puedes explicar tu trabajo con ellas.

## Añadir otro proyecto
1. Duplica proyectos/_plantilla como proyectos/nombre-corto.
2. Completa su README.md y sustituye sus imágenes de assets.
3. Copia una celda <td> de una tarjeta del README principal, cambia texto y rutas.
4. Para una nueva fila de dos proyectos, usa <tr> ... dos celdas ... </tr>. Si solo añades uno, puede ocupar una fila propia.
5. Enlaza con proyectos/nombre-corto/README.md. Dentro de la ficha, ../../README.md vuelve al perfil.
6. Revisa todos los enlaces después de renombrar carpetas.

## Animaciones y diseño
Los GIF ya están generados: no tienes que ejecutar Python ni instalar nada para publicarlos.
GitHub no ejecuta el CSS/JavaScript de la vista previa. El stack publicado usa una columna, etiquetas uniformes y sin tabla. La altura y recorte exacto de la foto pueden variar respecto a la maqueta; la versión real usa una imagen de ancho completo dentro de su celda.
Los badges dependen de Shields.io y requieren internet. Todas las demás imágenes están incluidas.

## Regenerar gráficos (opcional)
Necesitas Python y Pillow. Desde la raíz:

    python -m pip install -r scripts/requirements.txt
    python scripts/generar_recursos.py

Edita primero nombres, textos y frases en ese script. Incluye fuentes DejaVu y su licencia. Atención: regenerar sobrescribe las imágenes de muestra, incluida foto.png y las capturas; respalda tus imágenes reales antes de hacerlo.

## Ver antes de publicar
Abre preview/index.html en el navegador. Es una copia de vista previa del contenido de este paquete con enlaces internos a las fichas. No es el renderizador oficial de GitHub y no se sincroniza automáticamente si editas los Markdown. La referencia final es la pestaña Preview del archivo en GitHub.

## Archivos auxiliares
GUIA.md, scripts y preview no aparecen como contenido del perfil. Puedes conservarlos en el repositorio; nunca publiques .env ni credenciales. No necesitas GitHub Pages, npm, Vercel ni Render para mostrar este README.
