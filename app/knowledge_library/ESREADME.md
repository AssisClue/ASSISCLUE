cd C:\AI\ASSISCLUE
.\.venv\Scripts\Activate.ps1
uvicorn app.ui_local.library_ui.appdocs:app --host 127.0.0.1 --port 8001 --reload


En qué etapa estamos

Este bloque ya funciona.
No está “terminado perfecto”, pero ya sirve de verdad para:

registrar carpetas
escanear archivos
leer archivos
resumir
partir en chunks
pasar contenido útil a memoria
y, si querés, reconstruir Qdrant después
La idea más simple

Pensalo así:

1. Biblioteca

La app primero mira qué archivos existen.

2. Lectura

Después puede abrir un archivo y leerlo.

3. Preparación

Después puede resumirlo o partirlo en pedacitos.

4. Memoria

Y recién ahí puede pasarlo a la memoria real del sistema.

Dónde poner archivos ahora mismo
Carpetas importantes

Estas son las más importantes para vos:

Para dejar archivos tuyos
data/knowledge_library/libraries/
data/knowledge_library/collections/
Para roots registradas
data/knowledge_library/manifests/
Ahí se guarda el registro de carpetas conocidas por el bloque.
Para lo que produce el sistema
runtime/knowledge_library/maps/
runtime/knowledge_library/summaries/
runtime/knowledge_library/indexing/
En simple

Si hoy querés empezar ya, la opción más natural es:

poner tus archivos dentro de
data/knowledge_library/libraries/

Por ejemplo:

libros
PDFs
notas
recetas
documentos tuyos
Qué pasa cuando ponés algo ahí
No pasa magia automática total

El sistema no aprende todo solo por existir.

Lo correcto es esto:

Paso 1

Ponés archivos en una carpeta de library.

Paso 2

Esa carpeta tiene que estar registrada como root.
Eso lo maneja LibraryAdminService, que guarda nombre, ruta, tipo y tags.

Paso 3

Hacés scan.
Ahí la app arma el mapa de archivos encontrados.

Paso 4

Después podés:

leer
resumir
indexar
promover a memoria
Cómo sucede por dentro

Versión “10 años”:

Imaginá una biblioteca con 4 trabajos
Trabajo 1: “Anotar qué libros hay”

Eso es el Library Map.
Anota:

nombre
ruta
extensión
tamaño
hash
tags

Todavía no leyó el contenido.

Trabajo 2: “Abrir el libro”

Eso es Read On Demand.
La app abre el archivo cuando vos lo pedís.
Puede leer archivo, capítulo o buscar párrafos.

Trabajo 3: “Preparar un resumen”

Eso es Summarize / Index.
Hace resumen y lo parte en chunks.

Trabajo 4: “Guardar lo importante en el cerebro”

Eso es Promote To Context Memory.
Pasa chunks y resumen a context_memory.
Y después, si querés, Qdrant reconstruye el índice semántico desde ese JSON.

Lo más importante de entender
knowledge_library NO es el cerebro final

Es como una zona de biblioteca y preparación.

context_memory sí es la memoria real

Ahí vive la memoria/contexto del sistema.
Y Qdrant es el índice semántico, no la verdad principal.

Frase clave

Primero biblioteca, después lectura, después resumen/indexado, y recién al final memoria.

Cómo usarlo a tu favor
Caso 1: “Solo quiero que el asistente sepa que estos archivos existen”

Hacé esto:

poné archivos en data/knowledge_library/libraries/
registrá esa carpeta si hace falta
hacé scan

Resultado:
la app sabe que existen, pero todavía no los metió al cerebro.

Caso 2: “Quiero hablar de un archivo puntual”

Hacé esto:

buscás el archivo
lo abrís
lo leés o pedís resumen

Resultado:
uso puntual, sin cargarle todo a memoria.

Caso 3: “Este archivo sí vale la pena guardarlo para después”

Hacé esto:

summarize
index
promote to memory

Resultado:
ese contenido ya entra al sistema de memoria real.

Qué tunables tenemos

Los “tunables” son las perillas que podés mover.

En summarize
max_chars
max_summary_chars
Qué significa
max_chars: cuánto del archivo va a leer para resumir
max_summary_chars: qué tan largo puede ser el resumen
En index
chunk_size
chunk_overlap
write_vectors
make_summary
Qué significa simple
chunk_size: tamaño de cada pedazo
chunk_overlap: cuánto se pisan entre sí los pedazos
write_vectors: si querés escribir vectores directo
make_summary: si además del indexado querés resumen
En promote
rebuild_qdrant
Qué significa
False: pasás a memoria JSON, sin reconstruir Qdrant
True: además reconstruís el índice semántico
Qué usaría yo ahora

Para empezar fácil:

Carpeta

Usaría:

data/knowledge_library/libraries/
Flujo
poner archivos ahí
scan
abrir y leer
resumir solo lo que te interese
promover a memoria solo lo que valga la pena
Tunables recomendados al principio
max_summary_chars: dejalo normal, corto
chunk_size: valor medio
chunk_overlap: bajo o medio
write_vectors=False
rebuild_qdrant=False al principio

Después, cuando algo de verdad quieras dejar “bien metido”, hacés promote y si querés rebuild de Qdrant.

Qué cosas tenés que recordar
1

Poner archivos en una carpeta no alcanza si no hacés scan.

2

Ver un archivo en la UI no siempre significa que ya esté en memoria.

3

HOME / Library Files muestran lo que entró al library_map.

4

System Areas muestran carpetas reales del sistema, aunque no todo esté en library map.

5

Qdrant no es el comienzo del flujo; es una capa después.

Resumen bien corto
Hoy este bloque ya sirve para:
guardar archivos en carpetas tuyas
detectarlos con scan
leerlos
resumirlos
prepararlos
pasarlos a memoria real si querés
La carpeta más importante para empezar
data/knowledge_library/libraries/
Texto corto para un usuario nuevo del asistente

Podés usar esta sección para darle al asistente documentos, libros, notas y archivos tuyos. Primero el sistema detecta qué archivos existen, después puede abrirlos, resumirlos y, si vos querés, guardar lo importante en su memoria para usarlo más adelante. La mejor forma de aprovecharlo es poner tus archivos en la biblioteca, refrescar el escaneo y después abrir o resumir solo lo que realmente te interesa.

Si querés, en el siguiente te lo dejo todavía más práctico: “qué hago hoy, paso por paso, con 3 ejemplos reales”.





-------------------------------
-------------------------------




Sección 1: Library Files

Es la parte de tu biblioteca:

roots registradas
archivos escaneados
archivos que entraron al library_map
Sección 2: System Areas

Es la parte de carpetas reales de la app:

runtime
screenshots
web pages
memory
router
etc.
Entonces, ¿por qué ves 6 cajas?

Porque System Areas no es una sola carpeta.
Es un grupo de 6 áreas distintas, cada una con un propósito distinto.

1. Library Sources

Son carpetas donde vos ponés archivos tuyos.

libraries
collections
manifests
Qué significa
libraries = tus archivos principales
collections = grupos futuros/manuales
manifests = registro de roots conocidas

O sea: fuente de contenido.
Acá nace la biblioteca.

2. Knowledge Runtime

Son carpetas que guarda el propio bloque knowledge_library.

maps
summaries
indexing
Qué significa
maps = qué archivos encontró
summaries = resúmenes guardados
indexing = chunks, jobs, manifests

O sea: lo que produjo el bloque.

3. Display Actions

Es la parte de screenshots y análisis de pantalla.

screenshots
results
status
Qué significa

No es biblioteca.
Es otro bloque del sistema que guarda:

capturas
resultados
estado del runner

O sea: salida visual del sistema.

4. Web Tools

Es lo que guarda el bloque de navegador / Playwright.

pages
screenshots
Qué significa

Acá van:

HTML guardado
texto de páginas
capturas web

O sea: cosas traídas desde la web.

5. Router / Queues

Es la parte interna de colas y estado del sistema.

router_dispatch
Qué significa

No es para “leer libros”.
Es para ver:

colas
status
runtime interno

O sea: debug / tránsito interno.

6. Memory / Qdrant

Es la parte de memoria real y su índice.

memory
qdrant
Qué significa
memory = memoria/contexto
qdrant = índice semántico

O sea: la parte del cerebro y búsqueda semántica.

La diferencia más simple
Library Files

“Mis archivos de biblioteca”

System Areas

“Las carpetas reales del sistema”

Esa es la diferencia más importante.

Entonces, ¿qué estás viendo en la interface?

Pensalo así:

Home

Tiene 2 bloques:

A. Library Files

Para trabajar con:

archivos tuyos
archivos escaneados
resumen / index / promote
B. System Areas

Para inspeccionar:

carpetas reales del proyecto
outputs
runtime
memoria
screenshots
web captures
¿Cuántas pantallas reales tenemos hoy?

Yo diría que hoy hay 4 vistas principales:

1. Home

Vista general

2. File Detail

Detalle de un archivo de library

3. System Area

Vista de un área del sistema

4. System File

Detalle de un archivo encontrado en System Areas

Eso probablemente es lo que vos sentías como “4”.
No son 4 secciones, son más bien 4 tipos de pantalla.
