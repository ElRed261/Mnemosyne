# Roadmap personal de Data Engineering Zoomcamp

Para Andry · Mnemosyne · Versión 1.0 · Revisado el 27 de agosto de 2026

## Cómo usar este documento

Este es tu mapa de aprendizaje: define qué estudiar, en qué orden, qué construir y qué evidencia demuestra que aprendiste. Cubre los siete módulos del Zoomcamp, el taller de ingesta y el proyecto final, con un puente de fundamentos y complementos personales claramente separados.

No es una transcripción del curso ni un manual con todos los comandos de instalación. Cada práctica puede convertirse después en una lección textual paso a paso. No necesitas ver videos para seguir este roadmap; pueden servir de apoyo puntual.

La referencia es la estructura 2026 del [repositorio oficial](https://github.com/DataTalksClub/data-engineering-zoomcamp) y sus páginas de módulo. No mezcles tareas de distintas cohortes: consulta el [índice de 2026](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2026) cuando vayas a resolver un homework.

### Reglas de lectura

- **Troncal:** forma parte de la ruta principal del curso.
- **Refuerzo personal:** base o práctica que añadimos para que puedas aplicar lo aprendido.
- **Complemento:** amplía tu laboratorio, pero no bloquea el avance del curso.
- Una casilla se marca cuando puedes explicar y demostrar el resultado, no cuando has leído sobre él.
- Las prácticas propuestas aquí son personalizadas; no sustituyen los enunciados del homework oficial.
- Ninguna casilla presupone que ya completaste una materia. Tu avance real se registra con evidencia.

### Resultado final buscado

Construir un sistema que tome datos de una fuente, los almacene, los transforme en información consultable y actualice un dashboard. Debes poder reconstruirlo, detectar fallos, repetir una carga sin corromper los resultados y explicar sus límites.

El objetivo es una base práctica de Data Engineering; terminar un curso no equivale por sí solo a dominar sistemas de producción.

## Mapa general y prioridades

| Orden | Etapa | Profundidad en esta vuelta | Resultado principal |
| --- | --- | --- | --- |
| 1 | [B0. SQL, Python, terminal y Git](#b0-fundamentos-y-diagnóstico) | Base comprobada | Trabajar sin depender de copiar código a ciegas |
| 2 | [M1A. Docker, PostgreSQL e ingesta](#m1a-docker-postgresql-e-ingesta) | Dominar | Carga local reproducible y consultable |
| 3 | [M1B. GCP y Terraform](#m1b-google-cloud-y-terraform) | Dominar lo esencial | Infraestructura declarada y controlada |
| 4 | [M2. Orquestación con Kestra](#m2-orquestación-con-kestra) | Dominar | Pipeline programado y recuperable |
| 5 | [T1. Ingesta con dlt](#t1-ingesta-con-dlt) | Operativo | Cargas incrementales con estado y validación |
| 6 | [M3. BigQuery y warehouse](#m3-data-warehouse-y-bigquery) | Dominar | Tablas y consultas con diseño justificado |
| 7 | [M4. Analytics Engineering y dbt](#m4-analytics-engineering-con-dbt) | Dominar | Modelos analíticos, pruebas y documentación |
| 8 | [M5. Plataformas con Bruin](#m5-plataformas-de-datos-con-bruin) | Operativo | Entender una plataforma integrada |
| 9 | [M6. Procesamiento batch con Spark](#m6-procesamiento-batch-con-spark) | Operativo | Transformación por lotes y explicación de su ejecución |
| 10 | [M7. Streaming con Redpanda y PyFlink](#m7-streaming-con-redpanda-y-pyflink) | Operativo básico | Flujo de eventos con ventanas y recuperación |
| 11 | [PF. Proyecto final](#pf-proyecto-final) | Integrar y demostrar | Pipeline completo y reproducible |
| Intercalado | [X1. Floci en local y Uranus](#x1-complemento-floci-y-pruebas-en-uranus) | Complemento | Pruebas de APIs AWS sin depender de AWS real |
| Intercalado | [X2. Neovim](#x2-neovim-como-habilidad-secundaria) | Complemento ligero | Editar con comodidad sin frenar el aprendizaje |

**Dominar** significa poder construir, modificar y depurar un ejemplo pequeño consultando documentación. **Operativo** significa ejecutarlo, explicar sus piezas y resolver fallos comunes; no administrar todavía una plataforma grande.

Este documento no cambia tu calendario ni promete una nueva fecha de finalización. Mantén los bloques acordados de fin de semana mientras continúe inglés. Los bloques adicionales entre semana solo se habilitan cuando termine y exista disponibilidad real. No recuperes sesiones quitándote sueño.

Los complementos ocupan tiempo: se integran en prácticas existentes cuando sea posible; si añaden trabajo, se reprograma. No se suman automáticamente a una semana ya llena.

## Entorno personal y continuidad

La arquitectura acordada es local-first: estudias en el equipo disponible y Uranus sirve para pruebas remotas puntuales.

| Equipo | Uso en este roadmap | Límite |
| --- | --- | --- |
| tecnologia04 / Manjaro | Primera instalación y prácticas locales autorizadas | Proyecto personal aislado; ningún dato institucional |
| PCrda / CachyOS | Prácticas normales y cargas locales de Spark/Flink | No ejecutar todas las plataformas simultáneamente |
| Laptop / CachyOS | Continuar las mismas prácticas desde Git | Trabajar con muestras y recursos ajustados |
| Uranus / Ubuntu ARM64 | Almacenamiento y pruebas de integración pequeñas | Verificar imágenes ARM64; proteger servicios existentes |

### Lo que debes aprender a mantener

- [ ] Git comparte código, configuración sin secretos, documentación y pruebas.
- [ ] Los entornos Python y las imágenes se reconstruyen a partir de versiones fijadas.
- [ ] Los datasets se obtienen o regeneran mediante instrucciones reproducibles.
- [ ] Volúmenes, bases de datos, credenciales y estado de Terraform no se sincronizan mediante Git.
- [ ] Un cambio creado sin Internet solo estará en otro dispositivo después de transferirlo o sincronizarlo.
- [ ] Para estudiar sin conexión necesitas haber descargado previamente imágenes, dependencias y muestras.
- [ ] El repositorio privado del curso y el futuro repositorio del proyecto final tienen responsabilidades distintas.

En la PC institucional, un directorio o subvolumen organiza archivos, pero no constituye por sí solo una frontera de seguridad. Respeta la política autorizada y revisa permisos, montajes y servicios antes de ejecutar contenedores.

## B0. Fundamentos y diagnóstico

**Tipo:** refuerzo personal. **Entrada:** tus conocimientos actuales de Linux y SQL de IBM.

No necesitas repetir todo lo que ya sabes. Resuelve primero el diagnóstico y refuerza únicamente lo que no puedas explicar o ejecutar.

### B0.1. SQL relacional

- [ ] Tablas, filas, columnas, tipos, restricciones, claves primarias y foráneas.
- [ ] DDL y DML: crear estructuras y consultar o modificar datos.
- [ ] Filtros, ordenación, agregaciones, `GROUP BY` y `HAVING`.
- [ ] `INNER JOIN` y `LEFT JOIN`; relaciones uno a muchos y multiplicación accidental de filas.
- [ ] `NULL`, `IS NULL`, `COALESCE` y lógica de valores desconocidos.
- [ ] Subconsultas, CTE, `CASE` y conversiones de tipos.
- [ ] Fechas, timestamps y diferencia entre hora local y UTC.
- [ ] Ventanas: `ROW_NUMBER`, `RANK`, `LAG` y agregaciones con `OVER`.
- [ ] Transacciones: commit, rollback y por qué una carga parcial puede ser peligrosa.
- [ ] Diferencias de dialecto: no trasladar SQL de Oracle a PostgreSQL o BigQuery sin comprobarlo.

### B0.2. Python para mover datos

- [ ] Variables, colecciones, condiciones, bucles y funciones con entradas y salidas claras.
- [ ] Módulos, imports y ejecución de un script desde terminal.
- [ ] Archivos y rutas con `pathlib`; CSV, JSON y tipos de datos.
- [ ] Excepciones, mensajes de error y logs útiles.
- [ ] Peticiones HTTP: parámetros, estado de respuesta, timeout y paginación.
- [ ] Generadores e iteradores para no cargar todo en memoria.
- [ ] Pandas: selección, tipos, nulos, duplicados, agrupación y lectura por fragmentos.
- [ ] Diferencia entre un DataFrame en memoria y una tabla persistida.
- [ ] Entorno virtual, dependencias declaradas y archivo de bloqueo de versiones.
- [ ] Pruebas pequeñas con entradas conocidas y salidas esperadas.

No necesitas aprender desarrollo web, algoritmos avanzados ni todo Python antes de comenzar.

### B0.3. Terminal, Git y archivos

- [ ] Navegar por rutas y distinguir directorio actual, ruta absoluta y relativa.
- [ ] Leer archivos, buscar texto con `rg` y entender permisos básicos.
- [ ] Entender variables de entorno, procesos, puertos y códigos de salida.
- [ ] Distinguir la sintaxis de bash y fish cuando un ejemplo use variables o bucles.
- [ ] Usar `git status`, `diff`, `add`, `commit`, `log`, `fetch`, `pull` y `push`.
- [ ] Comprender rama, remoto, conflicto y exclusiones con `.gitignore`.
- [ ] Reconocer qué nunca debe aparecer en un commit: claves, contraseñas y datos privados.

### Diagnóstico práctico

1. Genera una muestra de tres estaciones ficticias y doce observaciones, con un duplicado y un dato ausente conocidos.
2. Con Python, informa cuántas filas son válidas, duplicadas e incompletas.
3. Escribe cinco consultas: filtro, agregado, join, CTE y ventana.
4. Compara el resultado con un cálculo manual sobre la muestra.
5. Explica una función y una consulta sin leerlas línea por línea.

**Evidencia:** script, consultas, muestra sintética pequeña y resultados esperados. Si todavía no hay motor SQL instalado, escribe y razona las consultas; su ejecución queda pendiente para M1A.

**Puedes avanzar cuando:** el código básico y los errores simples no te impiden concentrarte en Docker y en la carga de datos.

## M1A. Docker, PostgreSQL e ingesta

**Tipo:** troncal, primera parte del módulo 1. **Entrada:** B0 operativo.

El material incluye notas textuales de Docker, entornos, PostgreSQL, Pandas y SQLAlchemy. Úsalas como referencia principal. [Taller oficial Docker y SQL](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform/docker-sql).

### Qué aprender, en orden

- [ ] Imagen, contenedor, proceso y diferencias respecto a una máquina virtual.
- [ ] Construcción de una imagen: Dockerfile, dependencias, contexto y capas.
- [ ] Parámetros, variables, directorio de trabajo y ejecución de un script.
- [ ] Logs, estado, salida del proceso y acceso para diagnóstico.
- [ ] Puertos y redes: `localhost` dentro de un contenedor no es otro servicio.
- [ ] Bind mounts, volúmenes y persistencia al recrear un contenedor.
- [ ] Compose: servicios, nombres, redes, volúmenes y configuración del proyecto.
- [ ] PostgreSQL local: conexión, esquema, tipos y consultas de comprobación.
- [ ] Ingesta desde archivos con Python, Pandas y SQLAlchemy.
- [ ] Transformar un notebook exploratorio en un script parametrizado.
- [ ] Cargas por fragmentos, transacciones y control de duplicados.
- [ ] Separar parámetros del código y conservar credenciales fuera de Git.

### Práctica personalizada

1. Levanta una base de laboratorio local separada de cualquier servicio existente.
2. Crea las tablas de estaciones y observaciones.
3. Carga la muestra de B0 con un script que reciba la ruta del archivo.
4. Añade un segundo archivo y comprueba las filas incorporadas.
5. Repite el primer archivo: debe detectarse o evitarse la duplicación según una regla documentada.
6. Recrea únicamente el contenedor de práctica conservando su volumen y comprueba los datos.
7. Prueba una conexión con puerto erróneo y diagnostica el fallo mediante logs y configuración.

**Evidencia:** Dockerfile, Compose, script de ingesta, SQL y un README con parámetros y validaciones.

**Puedes avanzar cuando:** reconstruyes el ejemplo, sabes dónde persisten los datos y explicas por qué la aplicación llega a PostgreSQL.

**Preguntas de control:** ¿qué perderías sin volumen?, ¿por qué repetir una carga puede duplicar filas?, ¿por qué un contenedor no es una copia completa de tu PC?

pgAdmin puede ayudar a inspeccionar; no es obligatorio convertir su interfaz en el centro del aprendizaje.

## M1B. Google Cloud y Terraform

**Tipo:** troncal, segunda parte del módulo 1. **Entrada:** M1A.

Aprenderás a describir infraestructura y a distinguir los recursos de Google Cloud. [Módulo 1](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform).

### Qué aprender

- [ ] Proyecto, servicios habilitados, región y ubicación de los datos.
- [ ] Almacenamiento de objetos: bucket, objeto y prefijo; no confundirlos con tablas.
- [ ] Función de Cloud Storage y de un dataset de BigQuery.
- [ ] Identidad, cuenta de servicio y permisos mínimos necesarios.
- [ ] Autenticación y separación de credenciales por entorno.
- [ ] Terraform: provider, recurso, variable, output y dependencias.
- [ ] Ciclo `init`, `fmt`, `validate`, `plan` y `apply`.
- [ ] Estado de Terraform: función, protección, bloqueo y riesgo de copias divergentes.
- [ ] Cambios manuales y divergencia respecto al estado declarado.
- [ ] Revisar una eliminación antes de autorizarla; identificar sus recursos exactos.

### Práctica personalizada

1. Describe en papel qué recursos necesitas y para qué.
2. Prepara una configuración mínima de almacenamiento y dataset, con nombres parametrizados.
3. Comprueba sintaxis y revisa el plan.
4. Con cuenta, permisos y costes revisados, aplica únicamente al proyecto de laboratorio autorizado.
5. Ejecuta otro plan y comprueba que no propone cambios inesperados.
6. Explica cómo recuperarías el estado al continuar desde otro equipo sin guardarlo en Git.

**Evidencia:** configuración sin secretos, parámetros de ejemplo, explicación del estado y resumen del plan sin información sensible.

**Puedes avanzar cuando:** diferencias código, estado y recurso real; no confundes validar sintaxis con haber desplegado.

**Si no tienes cuenta GCP:** prepara y estudia la configuración, practica conceptos con recursos locales y registra la validación de nube como pendiente. Floci no ejecuta el provider de GCP.

**Costes:** revisa los controles disponibles antes de crear recursos. Un presupuesto de solo alertas no impide por sí mismo seguir gastando. [Documentación de presupuestos de Google Cloud](https://docs.cloud.google.com/billing/docs/how-to/budgets).

## M2. Orquestación con Kestra

**Tipo:** troncal. **Entrada:** ingesta de M1A; M1B para la variante GCP.

El módulo trabaja flujos, ejecución de Python, cargas a PostgreSQL y pipelines hacia GCP. También contiene apartados de IA y recursos adicionales, que aquí quedan después del flujo básico. [Módulo 2](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration).

### Qué aprender

- [ ] ETL frente a ELT; orquestar no es lo mismo que transformar.
- [ ] Flujo, tarea, dependencia, ejecución y estado.
- [ ] YAML, parámetros de entrada, variables, outputs y secretos.
- [ ] Ejecutar Python y SQL con dependencias controladas.
- [ ] Programación por calendario, zona horaria y disparadores.
- [ ] Reintentos, timeout y tratamiento de errores.
- [ ] Backfill: cargar periodos históricos de forma controlada.
- [ ] Idempotencia: repetir un periodo sin alterar indebidamente el resultado.
- [ ] Logs y trazabilidad desde la extracción hasta la tabla final.
- [ ] Variante local con PostgreSQL y variante con Cloud Storage/BigQuery.

### Práctica personalizada

1. Convierte tu carga manual en un flujo: obtener, validar, cargar y comprobar.
2. Añade una fecha como parámetro.
3. Ejecuta dos fechas y después repite una.
4. Introduce un archivo mal formado; el flujo debe señalar el fallo, no aparentar éxito.
5. Repara el archivo y reejecuta el periodo afectado.
6. Programa una ejecución de prueba y verifica su zona horaria.
7. Recorre un pequeño intervalo histórico sin lanzar cargas ilimitadas.

**Evidencia:** YAML, entradas de ejemplo, resultados por fecha y explicación de un fallo recuperado.

**Puedes avanzar cuando:** una ejecución normal no exige lanzar cada script manualmente y puedes reconstruir qué pasó en una ejecución fallida.

**Preguntas de control:** ¿qué tareas se pueden reintentar?, ¿qué ocurre si la fuente tarda?, ¿cómo evitas cargar dos veces el mismo periodo?

**Ampliación del módulo:** comprender las propuestas de Copilot/RAG y revisar un flujo sugerido por IA. No hace falta contratar inferencia ni desplegar esas integraciones para demostrar la orquestación básica.

## T1. Ingesta con dlt

**Tipo:** taller troncal; asistencia con IA como complemento. **Entrada:** Python e ingesta básica.

El taller de 2026 incluye extracción, normalización, destinos y validación asistida mediante dashboard/MCP. Snowflake aparece como ejemplo, no como obligación de añadir otra nube a esta ruta. [Taller de dlt](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/workshops/dlt.md).

### Qué aprender

- [ ] Fuente, recurso, pipeline y destino.
- [ ] Extracción desde API o archivos y paginación.
- [ ] Normalizar JSON anidado y entender las tablas resultantes.
- [ ] Inferencia de esquema, tipos y evolución del esquema.
- [ ] Diferencias entre añadir, reemplazar y combinar registros.
- [ ] Clave primaria, cursor incremental y estado de la carga.
- [ ] Dónde persiste ese estado y cómo se recupera al cambiar de equipo.
- [ ] Historial de cargas, filas rechazadas y comprobaciones de integridad.
- [ ] Cuándo dlt reduce trabajo respecto a mantener un cargador propio.

### Práctica personalizada

1. Usa primero un JSON local con estructura conocida; después prueba una API pública si está disponible.
2. Carga dos lotes parcialmente solapados.
3. Incluye un registro nuevo y la corrección de uno existente.
4. Comprueba que la estrategia elegida conserva el resultado esperado.
5. Introduce un campo nuevo y explica la evolución del esquema.
6. Comprueba qué sucede cuando ejecutas de nuevo el mismo lote.

**Evidencia:** pipeline, esquema resultante, comprobaciones de filas y descripción del estado incremental.

**Puedes avanzar cuando:** explicas qué datos se consideran nuevos y cómo recuperas una carga incompleta.

La IA puede proponer una extracción, pero debes revisar autenticación, paginación, tipos y pruebas. Un dashboard sin errores visibles no sustituye esas comprobaciones.

## M3. Data Warehouse y BigQuery

**Tipo:** troncal. **Entrada:** SQL, ingesta y conceptos de GCP.

El módulo incluye warehouse, particionado, clustering, funcionamiento general y temas avanzados de BigQuery ML. [Módulo 3](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse).

### Qué aprender

- [ ] OLTP frente a OLAP: operaciones de una aplicación frente a análisis.
- [ ] Data lake, warehouse y data mart: responsabilidades diferentes.
- [ ] CSV, JSON y Parquet; formatos por filas y columnares.
- [ ] Dataset, tabla, vista y tabla externa en BigQuery.
- [ ] Carga a tablas nativas y lectura de archivos externos.
- [ ] Tipos, fechas, nulos, arrays y estructuras cuando aparezcan en los datos.
- [ ] Particionado y eliminación de particiones innecesarias en una consulta.
- [ ] Clustering y elección de columnas según patrones de consulta.
- [ ] Bytes procesados, estimación previa y consulta solo de columnas necesarias.
- [ ] Ubicación, permisos y caducidad de datos de laboratorio.
- [ ] Separación conceptual entre almacenamiento y procesamiento.

### Práctica personalizada

1. Formula dos consultas: resumen diario por estación y comparación entre estaciones.
2. Carga una muestra en una tabla normal.
3. Prepara una variante particionada y, si se justifica, con clustering.
4. Compara resultados y bytes procesados con consultas equivalentes.
5. Documenta por qué elegiste ese diseño.

No inventes una mejora de rendimiento: una muestra pequeña puede no mostrar diferencias significativas. La evidencia válida es la medición y su interpretación.

**Evidencia:** SQL de creación y consulta, esquema y comparación explicada.

**Puedes avanzar cuando:** distingues objetos y tablas, eliges un diseño por una necesidad de consulta y verificas el resultado.

**Sin conexión o sin cuenta:** usa DuckDB para practicar SQL y Parquet; marca como pendiente la validación específica de BigQuery.

### Ampliación oficial, después de lo anterior

- [ ] Entender qué permite BigQuery ML.
- [ ] Reconocer entrenamiento, evaluación, predicción y separación de datos.
- [ ] Conocer el flujo de exportación/despliegue de un modelo.

Esta ampliación no exige convertir tu proyecto en uno de Machine Learning.

## M4. Analytics Engineering con dbt

**Tipo:** troncal. **Entrada:** SQL analítico y tablas cargadas.

La ruta oficial permite trabajar con DuckDB y dbt Core, además de la variante BigQuery. Empezar localmente encaja con tu continuidad entre equipos. [Módulo 4 y opciones de entorno](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering).

### Qué aprender

- [ ] Diferencia entre ingesta y transformación analítica.
- [ ] Modelado dimensional: hechos, dimensiones y granularidad de una fila.
- [ ] Claves naturales y sustitutas; relaciones y duplicación por joins.
- [ ] Capas de limpieza, modelos intermedios y modelos para consumo.
- [ ] Proyecto dbt: configuración, adaptador, conexiones y entornos.
- [ ] `source()`, `ref()` y dependencias entre modelos.
- [ ] SQL con Jinja; variables y macros sencillas.
- [ ] Materializaciones como vista, tabla e incremental.
- [ ] Seeds, paquetes y dependencias del proyecto.
- [ ] Pruebas de nulos, unicidad, relaciones y valores permitidos.
- [ ] Pruebas propias para una regla concreta del negocio.
- [ ] Documentación de columnas y linaje.
- [ ] Ejecución, selección de modelos, compilación y revisión de errores.
- [ ] Introducción a snapshots y cambios históricos, después del modelo básico.

### Práctica personalizada

1. Define qué representa una fila de observaciones antes de escribir modelos.
2. Construye una dimensión de estaciones y una tabla de hechos.
3. Añade un modelo de resumen diario con unidades y zona horaria documentadas.
4. Incorpora pruebas que detecten claves duplicadas y estaciones inexistentes.
5. Introduce un dato incorrecto y comprueba que una prueba falla.
6. Corrige el dato, reconstruye y verifica las métricas contra la muestra original.
7. Genera documentación y sigue el recorrido de una columna hasta su origen.

**Evidencia:** modelos, pruebas, documentación y explicación de la granularidad.

**Puedes avanzar cuando:** el resultado tiene significado analítico y sabes demostrar por qué un join no infla las métricas.

**Preguntas de control:** ¿por qué dbt no sustituye al extractor?, ¿qué representa cada fila?, ¿qué prueba detectaría una estación sin identificar?

## M5. Plataformas de datos con Bruin

**Tipo:** troncal. **Entrada:** ingesta, orquestación y modelado.

El módulo usa Bruin para conectar ingesta, transformación, planificación, calidad y metadatos. Contiene una plantilla de ejercicios y notas textuales. [Módulo 5](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/05-data-platforms).

### Qué aprender

- [ ] Proyecto, pipeline y asset.
- [ ] Assets de SQL, Python e ingesta declarativa.
- [ ] Conexiones y entornos separados.
- [ ] Configuración del pipeline y dependencias entre assets.
- [ ] Variables y ventanas de fechas para una ejecución.
- [ ] Capas de ingesta, preparación y reportes.
- [ ] Validación, ejecución, controles de calidad y linaje.
- [ ] Diferencia entre ejecutar localmente y desplegar en una plataforma administrada.
- [ ] Qué puede hacer una integración MCP y qué permisos no debería recibir.

### Práctica personalizada

1. Completa primero la plantilla del módulo con un destino local.
2. Ejecuta validaciones y revisa sus dependencias.
3. Repite una pequeña carga meteorológica con dos o tres assets.
4. Añade una regla que rechace un dato inválido.
5. Compara por escrito el resultado con la combinación Kestra + dlt + dbt.

**Evidencia:** pipeline, assets y una decisión breve sobre cuándo usarías cada enfoque.

**Puedes avanzar cuando:** explicas las responsabilidades que integra Bruin y ejecutas una práctica completa.

**Límite personal:** comprender Bruin no obliga a migrar todo Mnemosyne. Cloud y MCP se estudian como extensiones; no requieren abrir cuentas, pagar ni conectar agentes con permisos amplios para aprobar tu práctica local.

## M6. Procesamiento batch con Spark

**Tipo:** troncal. **Entrada:** Python, SQL y Parquet.

La ruta cubre DataFrames, SQL, ejecución distribuida, agrupaciones, joins y conexiones con GCP. Los RDD aparecen como ampliación opcional. [Módulo 6](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-batch).

### Qué aprender

- [ ] Cuándo un trabajo batch es suficiente y cuándo Spark aporta valor.
- [ ] Driver, executors, tareas y particiones.
- [ ] SparkSession, DataFrame y esquema explícito.
- [ ] Lectura y escritura de CSV/Parquet.
- [ ] Selección, filtros, columnas derivadas, agrupaciones y joins.
- [ ] Spark SQL y vistas temporales.
- [ ] Transformaciones frente a acciones y evaluación diferida.
- [ ] Plan de ejecución, stages y shuffle.
- [ ] Joins con tablas pequeñas y distribución desigual de claves.
- [ ] Reparticionado, reducción de particiones y demasiados archivos pequeños.
- [ ] Caché con propósito; límites de memoria y riesgos de traer todo al driver.
- [ ] Empaquetar y ejecutar un job con parámetros.
- [ ] Conexión con Cloud Storage y BigQuery; concepto de ejecución con Dataproc.

### Práctica personalizada

1. Genera una muestra reproducible suficientemente variada, sin intentar saturar el equipo.
2. Calcula el mismo resumen meteorológico con SQL local y con Spark.
3. Compara claves, conteos y valores; define tolerancias si hay decimales.
4. Inspecciona el plan de un join y una agrupación.
5. Cambia el particionado y observa los archivos resultantes.
6. Ejecuta el trabajo como script, no únicamente como notebook.

**Evidencia:** job, esquema, comparación de resultados y explicación de una operación costosa.

**Puedes avanzar cuando:** entiendes por qué un job mueve datos y puedes depurar un ejemplo pequeño.

**Entorno:** prioriza PCrda o un nodo x86 con recursos disponibles. No fuerces un clúster pesado en Uranus. La compatibilidad de Spark, Java y Python debe comprobarse en el módulo; si necesita un entorno separado, documenta y acuerda ese cambio sin alterar la base de Mnemosyne automáticamente.

**Ampliaciones:** RDD, `mapPartitions` y ejecución administrada. No levantes Dataproc solo por completar una casilla sin revisar coste y limpieza de recursos.

## M7. Streaming con Redpanda y PyFlink

**Tipo:** troncal. **Entrada:** Python, SQL, Docker y nociones de particionado.

El módulo vigente dirige al taller de Redpanda, Python, Flink y PostgreSQL. La teoría de Kafka con Java y los ejemplos de otros años se presentan aparte. No necesitas recorrerlos todos antes de construir el pipeline actual. [Módulo 7](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming).

### Qué aprender

- [ ] Batch frente a streaming: necesidad real de baja latencia.
- [ ] Evento, productor, broker, topic, partición y consumidor.
- [ ] Clave del mensaje, offset, grupo de consumidores y retención.
- [ ] Orden dentro de una partición, no orden global garantizado.
- [ ] Serialización y contrato de datos entre productor y consumidor.
- [ ] Papel de Redpanda como broker compatible con la API de Kafka.
- [ ] Fuente, transformación y destino de un trabajo PyFlink.
- [ ] Tiempo del evento frente al tiempo de procesamiento.
- [ ] Ventanas fijas, deslizantes y de sesión.
- [ ] Watermarks y tratamiento explícito de eventos tardíos.
- [ ] Estado, checkpoints y recuperación de un job.
- [ ] Entregas repetidas, idempotencia y escritura por clave en PostgreSQL.
- [ ] Diferenciar garantías del motor de garantías de extremo a extremo.

Estas capacidades se practican en el [taller textual de PyFlink](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming/workshop).

### Práctica personalizada

1. Produce eventos sintéticos con identificador, estación, timestamp y medida.
2. Consúmelos y valida el esquema.
3. Calcula un agregado por ventana y guárdalo en una base local de laboratorio.
4. Envía un evento duplicado y otro fuera de orden.
5. Documenta qué ocurre según la configuración de ventanas y destino.
6. Interrumpe de forma controlada solo tu job de práctica, recupéralo y comprueba el resultado.
7. Compara las ventanas con un cálculo batch sobre los mismos eventos.

**Evidencia:** productor, job, esquema, configuración y pruebas de duplicación, retraso y recuperación.

**Puedes avanzar cuando:** explicas por qué una ventana da ese resultado y qué se conserva al reiniciar.

**Preguntas de control:** ¿qué pasa si escribes en la base pero no confirmas el avance?, ¿qué haces con un evento demasiado tarde?, ¿necesita realmente streaming tu proyecto final?

**Ampliación posterior:** Avro, evolución de esquemas, Schema Registry, Kafka Streams y ksqlDB. Son contexto útil del ecosistema; no sustituyen el taller actual ni justifican añadir Java como requisito inicial.

## PF. Proyecto final

**Tipo:** integración del curso. **Entrada:** las piezas que necesitas funcionan por separado.

La propuesta personal es un proyecto nuevo de datos meteorológicos del Caribe, con fuentes públicas o una muestra sintética claramente identificada. No reutilices datos institucionales ni un proyecto previo de otro curso.

La rúbrica pide un pipeline completo, almacenamiento, warehouse, transformaciones, visualización y reproducibilidad. Prohíbe NYC Taxi para el proyecto final, aunque se use en las prácticas. El dashboard debe tener al menos dos visualizaciones. [Requisitos y rúbrica](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/projects).

### Decisiones antes de construir

- [ ] Formular dos preguntas concretas que los datos puedan responder.
- [ ] Elegir una fuente y comprobar licencia, disponibilidad, unidades y límites de acceso.
- [ ] Definir el significado de una fila y la clave de unicidad.
- [ ] Elegir frecuencia batch o streaming y justificarla.
- [ ] Especificar qué hacer ante datos ausentes, correcciones y fallos de la fuente.
- [ ] Definir alcance mínimo y qué mejoras quedan fuera.

Para tu primera entrega, batch es una opción razonable si las preguntas no exigen tiempo real. Haber estudiado streaming no obliga a usarlo.

### Arquitectura de referencia

| Responsabilidad | Elección sencilla para el proyecto |
| --- | --- |
| Extraer datos | Python o dlt, según lo que reduzca complejidad |
| Conservar originales | Cloud Storage para la variante GCP; almacenamiento local/S3 emulado para desarrollo |
| Coordinar ejecuciones | Kestra |
| Consultar y modelar | BigQuery + dbt; DuckDB para desarrollo local cuando corresponda |
| Mostrar resultados | Una herramienta de dashboard, no varias |
| Reproducir infraestructura | Terraform, configuración versionada y dependencias fijadas |
| Comprobar resultados | Pruebas de datos y de transformación |

Es una recomendación, no una obligación de meter todas las herramientas del curso en el mismo sistema.

### Construcción por entregas

1. **Diseño:** preguntas, fuente, esquema y responsabilidades.
2. **Recorrido mínimo:** un archivo llega hasta una consulta y una visualización.
3. **Repetibilidad:** parámetros, varias fechas y reconstrucción desde un clon limpio.
4. **Fiabilidad:** validación, reintentos, deduplicación y recuperación.
5. **Modelo analítico:** claves, métricas, pruebas y diseño de tablas justificado.
6. **Presentación:** dos visualizaciones claras, README y evidencia de ejecución.

### Criterios personales de aceptación

- [ ] Otra persona puede entender qué problema resuelve.
- [ ] Existe una muestra de prueba pequeña o un generador reproducible.
- [ ] Una ejecución normal no requiere pasos manuales ocultos.
- [ ] La repetición del mismo periodo produce el resultado previsto.
- [ ] Los registros inválidos se rechazan o aíslan con una explicación.
- [ ] Los originales permiten investigar de dónde sale una métrica.
- [ ] Las credenciales no aparecen en el repositorio ni en capturas.
- [ ] Los datos y resultados se verifican contra una muestra conocida.
- [ ] Las instrucciones funcionan en un entorno limpio compatible.
- [ ] Se documentan límites, costes posibles y cierre seguro de los recursos.

Prepara preferiblemente un repositorio específico para presentar el proyecto; conserva el repositorio del curso como cuaderno de aprendizaje. Revisa la rúbrica vigente antes de enviar. Un emulador no acredita por sí solo los criterios de nube o de rendimiento.

La modalidad autónoma permite estudiar y construir el proyecto, pero el certificado depende de participar en una cohorte y cumplir sus condiciones, incluida la revisión de compañeros. [Modalidades y certificación](https://github.com/DataTalksClub/data-engineering-zoomcamp).

## X1. Complemento Floci y pruebas en Uranus

**Tipo:** personal y opcional. No es un módulo oficial ni está desplegado por este documento.

Floci emula APIs de AWS y publica imágenes para amd64 y arm64. Sirve para probar integraciones; no sustituye a GCP, BigQuery, Kafka o una evaluación de AWS real. [Proyecto](https://github.com/floci-io/floci), [arquitecturas de las imágenes](https://floci.io/floci/configuration/docker-images/).

### Qué aprender con él

- [ ] Diferenciar una API de almacenamiento de objetos de un sistema de archivos.
- [ ] Usar bucket, clave, prefijo y endpoint configurable.
- [ ] Probar un cliente con credenciales ficticias y sin apuntar a AWS real.
- [ ] Repetir la misma prueba en local y en un servicio remoto privado.
- [ ] Separar configuración de Terraform para emulación y para nube real.
- [ ] Comprobar persistencia después de reiniciar.
- [ ] Como ampliación, trabajar con una cola SQS y tratamiento de mensajes fallidos.

### Inserción en la ruta

| Práctica | Momento | Prueba de aceptación |
| --- | --- | --- |
| F1. Objetos y persistencia | Después de M1A | Subir y recuperar un archivo idéntico después de reiniciar |
| F2. Infraestructura emulada | Después de M1B | Crear recursos declarados y obtener un segundo plan sin cambios |
| F3. Ingesta remota | Durante M2/T1 | Escribir originales y resultados validados sin duplicar una carga |
| F4. Cola y recuperación | Después del pipeline básico; opcional | Reprocesar un mensaje fallido sin duplicar el efecto final |

Reserva orientativa: tres prácticas de dos horas y una cuarta opcional. Si no caben en los bloques disponibles, se aplazan; no son requisito para empezar el Zoomcamp.

### Fronteras de seguridad

- Probar primero en tecnologia04 o en otro equipo local autorizado.
- En Uranus, verificar arquitectura, recursos y puertos antes de proponer un despliegue.
- Usar proyecto Compose, red y volumen propios, con versión de imagen fijada.
- Enlazar a loopback y acceder por un túnel SSH, que puede usar Tailscale como transporte.
- No montar el socket de Docker ni usar modo privilegiado para las primeras prácticas.
- No modificar CasaOS, Caddy ni otros servicios existentes.
- No recrear `arca-pg`, `n8n` ni `9router`.
- Tratar el PostgreSQL que se administre mediante CasaOS como servicio externo protegido.
- Conservar MinIO como alternativa; no ejecutar ambos por costumbre ni migrar datos automáticamente.

La imagen de Floci usa almacenamiento en memoria por defecto. Para conservar las pruebas, hay que seleccionar un modo persistente y montar su ruta de datos; un volumen aislado no basta si el modo sigue siendo memoria. [Configuración de persistencia](https://floci.io/floci/configuration/storage/).

El perfil `aws-lab` continúa siendo una propuesta de integración. No supongas que existe un comando de Mnemosyne para Floci hasta que se implemente y pruebe.

## X2. Neovim como habilidad secundaria

**Tipo:** complemento. Aprende una operación pequeña durante el trabajo, no un sistema entero de plugins.

1. Abrir, guardar y salir.
2. Distinguir modo normal, inserción y selección.
3. Moverse por palabras y líneas.
4. Buscar texto y repetir la búsqueda.
5. Copiar, borrar, pegar, deshacer y rehacer.
6. Editar SQL, YAML y Python sin perder indentación.
7. Después: navegación por errores, formato y apoyo del lenguaje.

Utiliza la configuración aislada de Mnemosyne; no sobrescribas tu configuración personal. Si el editor bloquea una práctica, termina con un editor conocido y vuelve a Neovim después.

## Hábitos técnicos que atraviesan todos los módulos

Estas son comprobaciones personales de calidad, no una lista adicional de plataformas que instalar.

- [ ] **Contrato de datos:** saber qué campos, tipos, unidades y claves se esperan.
- [ ] **Calidad:** comprobar nulos, duplicados, rangos y referencias entre tablas.
- [ ] **Idempotencia:** definir qué significa repetir una operación correctamente.
- [ ] **Observabilidad:** registrar fecha, entrada, filas procesadas, duración y estado.
- [ ] **Pruebas:** combinar una muestra pequeña conocida con comprobaciones de integración.
- [ ] **Reproducibilidad:** fijar dependencias y evitar rutas personales dentro del código.
- [ ] **Seguridad:** mínimos permisos y separación de datos, secretos y código.
- [ ] **Recuperación:** distinguir reintentar, restaurar un respaldo y reconstruir desde la fuente.
- [ ] **Documentación:** dejar instrucciones que funcionen desde otro dispositivo.
- [ ] **Decisiones:** explicar por qué se eligió una herramienta y qué alternativa se descartó.

Prueba también tres fallos recurrentes: fuente inaccesible, esquema inesperado y carga repetida. La respuesta del sistema debe ser visible y verificable.

## Método de estudio y registro del avance

### Una sesión de dos horas

- 10 minutos: leer el punto actual y elegir un resultado pequeño.
- 20 minutos: teoría y ejemplo mínimo.
- 65 minutos: práctica, incluyendo una variante que tú modifiques.
- 10 minutos: pausa, colocada donde sea más útil.
- 15 minutos: comprobación, evidencia y registro del próximo paso.

Si no alcanza el tiempo, registra el avance parcial. No marques la etapa como terminada porque el programa abrió o porque una IA generó los archivos.

### Escala de dominio

| Nivel | Qué puedes demostrar |
| --- | --- |
| 0 | No lo he trabajado |
| 1 | Puedo explicarlo y reproducir un ejemplo guiado |
| 2 | Puedo adaptarlo a un caso parecido y verificarlo |
| 3 | Puedo diagnosticar un fallo sencillo y justificar la solución |

Busca nivel 2 en los contenidos principales y nivel 3 en SQL, ingesta, pruebas y continuidad. Esta es una guía personal de evaluación, no una nota oficial.

### Continuidad con Mnemosyne

Si el kit ya está instalado y revisado, utiliza sus comandos desde la raíz del repositorio:

```bash
./mnemo doctor
./mnemo start
```

Al cerrar, registra el resultado, el siguiente objetivo, el próximo comando exacto y su salida esperada en `CURRENT.md`. Después usa el flujo de cierre del kit:

```bash
./mnemo end
```

Sin conexión, un commit local conserva el avance; no implica que ya haya llegado al otro equipo. Sincroniza cuando vuelva la red y revisa cualquier divergencia sin forzar ni borrar cambios.

Si `mnemo` no existe, no intentes ejecutar estos comandos: primero se prepara el kit con el procedimiento de instalación correspondiente.

### Registro sugerido

| Etapa | Estado | Evidencia | Próximo paso |
| --- | --- | --- | --- |
| B0 | Por comprobar | Pendiente | Resolver diagnóstico |
| M1A | Pendiente | Pendiente | Carga local mínima |
| M1B | Pendiente | Pendiente | Configuración de infraestructura |
| M2 | Pendiente | Pendiente | Flujo parametrizado |
| T1 | Pendiente | Pendiente | Dos lotes solapados |
| M3 | Pendiente | Pendiente | Diseño de tablas y consultas |
| M4 | Pendiente | Pendiente | Modelo y pruebas |
| M5 | Pendiente | Pendiente | Pipeline integrado pequeño |
| M6 | Pendiente | Pendiente | Job batch comparado |
| M7 | Pendiente | Pendiente | Ventana con eventos de prueba |
| PF | Pendiente | Pendiente | Preguntas y fuente |

Los estados son un punto de partida, no una evaluación de tus conocimientos actuales. Actualízalos después del diagnóstico.

## Cómo usar este archivo con OpenCode u otra IA

Este Markdown es material de referencia. No instala una Skill, no concede permisos y no configura dispositivos automáticamente.

Colócalo junto a la documentación de tu repositorio y proporciona también `AGENTS.md` y `CURRENT.md` si existen. Puedes usar esta instrucción:

```text
Lee AGENTS.md, CURRENT.md y Roadmap_Data_Engineering_Zoomcamp_Andry.md.
Comprueba el estado real del repositorio antes de asumir que algo está instalado.
Identifica la siguiente competencia pendiente y prepara una sola lección textual.

Para esa lección necesito:
1. Objetivo y conocimientos previos.
2. Explicación clara con un ejemplo pequeño.
3. Comandos exactos, adaptados al dispositivo y al shell.
4. Resultado esperado y cómo comprobarlo.
5. Un ejercicio que yo deba modificar o resolver.
6. Fallos comunes y diagnóstico.
7. Evidencia que guardar y siguiente paso.

No generes todas las soluciones de los ejercicios antes de que lo intente.
No marques tareas como completadas sin resultados comprobados.
No instales, sobrescribas configuraciones, despliegues recursos ni alteres
servicios persistentes sin explicar el plan y obtener la confirmación necesaria.
No uses datos institucionales. No dependas de videos ni de Uranus para cada sesión.
No añadas herramientas nuevas si las actuales permiten completar la competencia.
```

La primera lección debe ser el diagnóstico de B0, salvo que la evidencia existente muestre que ya lo superaste. No es necesario preparar Spark, Flink y Floci antes de empezar Docker.

## Qué dejar para después del Zoomcamp

No lo uses como lista de prerrequisitos. Son posibles continuaciones:

- CI/CD y ejecución automática de pruebas.
- Cambios de datos mediante CDC y herramientas específicas.
- Formatos de tablas de lakehouse y evolución de esquemas a mayor escala.
- Catálogos, gobierno y observabilidad más completos.
- Operación de clústeres y Kubernetes.
- Profundización en AWS o en otra nube.
- Sistemas de datos para ML y plataformas internas para equipos.

Elige una continuación según una necesidad concreta de tu proyecto o una oportunidad de aprendizaje. No necesitas dominar todas para terminar esta ruta.

## Glosario mínimo

- **Pipeline:** secuencia que lleva datos desde una entrada hasta un resultado.
- **Ingesta:** incorporar datos desde una fuente a un sistema de destino.
- **Orquestación:** coordinar cuándo y en qué orden se ejecuta el trabajo.
- **Esquema:** estructura esperada de los datos.
- **Granularidad:** qué representa exactamente una fila.
- **Idempotencia:** repetir una operación sin producir efectos adicionales indebidos.
- **Backfill:** procesar periodos históricos que faltaban.
- **Linaje:** recorrido y dependencias de un dato desde su origen.
- **Partición:** división de datos o de trabajo; su significado concreto depende de la herramienta.
- **Checkpoint:** estado guardado que permite recuperar una ejecución.
- **Staging:** entorno de pruebas de integración; también puede nombrar una capa intermedia de datos.
- **Criterio de aceptación:** comprobación observable que permite dar una tarea por terminada.

## Lista final de capacidades

- [ ] Puedo obtener datos de archivos y APIs con errores controlados.
- [ ] Puedo almacenarlos y consultarlos con SQL.
- [ ] Puedo reconstruir mi entorno desde el código y las dependencias declaradas.
- [ ] Puedo programar cargas y repetir periodos sin corromper resultados.
- [ ] Puedo modelar datos y probar sus reglas.
- [ ] Puedo justificar cuándo usar batch y cuándo streaming.
- [ ] Puedo explicar una consulta, un job y una decisión de infraestructura.
- [ ] Puedo continuar desde otro equipo sin perder código ni confundirlo con datos persistentes.
- [ ] Puedo mostrar un proyecto completo y documentar sus limitaciones.

El siguiente paso es pequeño: comprobar la base y completar una primera carga local. El resto del roadmap se construye sobre esa evidencia.
