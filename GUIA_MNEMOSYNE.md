# Mnemosyne: manual local-first del laboratorio de Data Engineering

## 1. Decisión definitiva

El laboratorio funciona **local-first**. Cada computadora conserva una copia completa del código, documentación y entorno reproducible. Git es la memoria compartida; Uranus es un servidor de staging para pruebas semirreales, no el escritorio diario.

Esta arquitectura busca cuatro resultados:

1. poder estudiar sin Internet;
2. reconstruir dependencias de la misma forma en cada nodo;
3. terminar una sesión con un punto de continuación inequívoco;
4. evitar que un servicio remoto, una configuración de editor o un dataset bloquee el curso.

La automatización se llama **Mnemosyne** y su interfaz estable es `./mnemo`.

## 2. Estado real de Uranus

- `arca-pg` fue eliminado y no debe recrearse.
- `n8n` fue eliminado y no debe recrearse.
- `9router` fue eliminado y no debe recrearse.
- PostgreSQL se instalará desde la tienda de CasaOS. Mnemosyne lo considera un servicio externo: puede comprobar su puerto o abrir un túnel, pero no lo crea, detiene ni elimina.
- Caddy y los demás servicios existentes quedan fuera del alcance del curso.
- El único servicio opcional declarado por Mnemosyne es un almacén de objetos S3 de estudio, bajo el perfil Compose `datalake`.

## 3. Función de cada nodo

| Nodo | Arquitectura | Función | Regla principal |
|---|---:|---|---|
| PCrda | x86_64 | estación principal | cargas locales pesadas y trabajo cómodo |
| laptop | x86_64 | estación móvil | misma copia reproducible, sin estado especial |
| tecnologia04 | x86_64 | estación institucional autorizada | proyecto aislado; nunca mezclar datos de INDOMET |
| Uranus | ARM64 | staging | servicios puntuales y pruebas de integración |

No existe un “equipo maestro” que contenga archivos irrepetibles. PCrda es principal por comodidad y potencia, pero Git conserva el estado compartido.

## 4. Qué se sincroniza

Sí se versiona:

- código fuente;
- SQL, Terraform y archivos Compose sin secretos;
- ejercicios y documentación;
- pruebas;
- `CURRENT.md`, que indica exactamente dónde continuar;
- `uv.lock`, que fija el entorno Python.

No se versiona:

- `.env`, tokens, contraseñas y claves;
- `.venv` y cachés;
- datasets crudos o grandes;
- bases de datos y volúmenes Docker;
- `.terraform`, estados y variables reales de Terraform;
- información institucional.

Git no puede transportar a otro equipo un commit que todavía solo exista sin conexión en el equipo anterior. En ese caso el trabajo está seguro localmente, pero hay que ejecutar `./mnemo sync` desde ese nodo cuando vuelva la red antes de esperar verlo en otro.

## 5. Aislamiento en tecnologia04

La opción predeterminada es sencilla:

1. una carpeta personal dedicada para el repositorio;
2. entorno Python dentro de `.venv` administrado por `uv`;
3. contenedores con nombre de proyecto propio;
4. datos de práctica dentro de rutas ignoradas por Git;
5. ninguna credencial ni dataset de INDOMET.

Si se desea separar también configuraciones de usuario, Distrobox puede usar un HOME alternativo. Esto organiza los archivos, pero no debe tratarse como una frontera de seguridad. Para aislamiento fuerte se necesita una máquina virtual aprobada por la institución. Un subvolumen Btrfs —posiblemente el término que se había olvidado— organiza almacenamiento y snapshots, pero tampoco aísla procesos.

No se modifica el sistema institucional a ciegas: `bootstrap` siempre muestra primero su plan y solo instala con `--apply`.

## 6. Primera preparación del repositorio

El repositorio personal recomendado es `andry-de-zoomcamp`, privado. El repositorio público de DataTalksClub sirve como fuente del curso, no como lugar para guardar secretos o trabajo personal.

Para que una IA prepare el repositorio, darle esta instrucción:

> Usa la Skill `$manage-mnemosyne-data-lab`. Inspecciona primero mi repositorio `andry-de-zoomcamp`, muestra la vista previa y después instala la plantilla Mnemosyne sin sobrescribir archivos distintos. Conserva mis cambios y valida el resultado.

La instalación de la plantilla agrega, entre otros:

- `AGENTS.md`: contrato operativo para cualquier IA;
- `GUIA_MNEMOSYNE.md`: este manual;
- `CURRENT.md`: punto exacto de reanudación;
- `mnemo` y `scripts/mnemo.py`: interfaz de automatización;
- `mnemosyne.toml`: nodos, comprobaciones y conexión con Uranus;
- `pyproject.toml`, `.python-version` y `uv.lock`: entorno Python;
- `tools/nvim/init.lua`: configuración didáctica aislada;
- `infra/uranus/compose.yaml`: staging opcional.

Después de confirmar estos archivos, se hace el primer commit y push.

## 7. Incorporar cada dispositivo

Primero se clona el repositorio personal. Dentro de él, se ejecuta una sola orden según el nodo:

```bash
# PC de escritorio
./mnemo onboard PCrda --apply

# Laptop
./mnemo onboard laptop --apply

# PC del trabajo
./mnemo onboard tecnologia04 --apply

# VPS
./mnemo onboard Uranus --profile uranus --apply
```

`onboard` combina:

1. detección de la distribución;
2. presentación e instalación confirmada de herramientas;
3. instalación de Python 3.12 con `uv` cuando corresponde;
4. registro local del nodo;
5. sincronización segura por fast-forward;
6. reconstrucción exacta de dependencias con `uv.lock`;
7. presentación de `CURRENT.md`.

Sin `--apply`, la orden es una vista previa y no instala paquetes. En tecnologia04 conviene revisar el plan con el responsable o la política local antes de confirmarlo. `--yes` existe para automatización no interactiva, pero solo debe usarse después de revisar el plan en un equipo propio.

## 8. Rutina de cada sesión

### Abrir

```bash
cd ~/ruta/andry-de-zoomcamp
./mnemo start
```

`start`:

- identifica el nodo;
- se niega a ocultar una operación Git inconclusa;
- sincroniza solo mediante fast-forward si el árbol está limpio y hay red;
- funciona sin conexión si el remoto no responde;
- reconstruye dependencias con `uv sync --locked`;
- muestra el último resultado y el siguiente comando de `CURRENT.md`.

Para declarar de antemano que no habrá red:

```bash
./mnemo start --offline
```

### Trabajar

La unidad mínima de trabajo es:

> objetivo pequeño → ejecución → comprobación → evidencia

No abrir otro tema hasta obtener un resultado verificable. Los datasets descargados se guardan bajo `data/` y no entran en Git.

### Cerrar

La forma guiada es:

```bash
./mnemo end
```

La forma explícita y reutilizable por una IA es:

```bash
./mnemo end \
  --done "Resultado que realmente comprobé" \
  --next "Siguiente objetivo pequeño" \
  --command "comando exacto para continuar" \
  --expected "señal concreta de éxito" \
  --notes "bloqueo o contexto importante"
```

Antes de crear el checkpoint, `end`:

1. actualiza `CURRENT.md` de forma atómica;
2. ejecuta Ruff y las pruebas configuradas;
3. revisa rutas y patrones comunes de secretos;
4. muestra los archivos que incluirá;
5. pide confirmación;
6. crea un commit;
7. intenta hacer push sin reescribir historial.

Si no hay red:

```bash
./mnemo end --offline
```

El commit queda local. Al recuperar conexión:

```bash
./mnemo sync
```

## 9. Comandos disponibles

| Comando | Función |
|---|---|
| `./mnemo doctor` | diagnóstico de solo lectura |
| `./mnemo onboard NODO --apply` | preparación completa de un nodo nuevo |
| `./mnemo bootstrap` | vista previa de paquetes del sistema |
| `./mnemo start` | sincronizar, reconstruir y reanudar |
| `./mnemo current` | mostrar únicamente el punto de continuación |
| `./mnemo end` | verificar y cerrar con checkpoint |
| `./mnemo sync` | sincronizar un árbol limpio |
| `./mnemo device show` | mostrar identidad y rol local |
| `./mnemo edit` | abrir Neovim con configuración aislada |
| `./mnemo remote status` | consultar el staging de Mnemosyne |
| `./mnemo remote up datalake` | iniciar el almacén S3 de estudio |
| `./mnemo remote stop datalake` | detenerlo sin borrar datos |
| `./mnemo remote logs datalake` | ver sus últimas líneas de registro |
| `./mnemo remote tunnel datalake` | abrir puertos S3 por SSH |
| `./mnemo remote tunnel postgres` | acceder al PostgreSQL de CasaOS por SSH |

## 10. Neovim sin convertirlo en otro curso

```bash
./mnemo edit
```

La orden usa `NVIM_APPNAME=mnemosyne-nvim`, por lo que no toca una configuración existente de Neovim. La plantilla es deliberadamente pequeña y sin plugins obligatorios.

Aprendizaje pasivo recomendado:

1. sesión 1: `i`, `Esc`, `:w`, `:q`;
2. sesión 2: `h`, `j`, `k`, `l` y `w`, `b`;
3. sesión 3: `/texto`, `n`, `N`;
4. sesión 4: `dd`, `yy`, `p`, `u`;
5. después: un solo movimiento o comando nuevo por sesión.

El objetivo es editar ejercicios, no mantener una distribución compleja de Neovim.

## 11. Uranus como staging

### PostgreSQL

PostgreSQL pertenece a CasaOS. Mnemosyne no lo incluye en Compose y no usa `down`, `rm` ni borrado de volúmenes contra él.

Para conectarse sin publicar el puerto a Internet:

```bash
./mnemo remote tunnel postgres
```

La configuración predeterminada expone en el equipo local el puerto `15432` y lo dirige al `5432` de loopback en Uranus. La contraseña vive fuera de Git.

### Almacén de objetos S3

`infra/uranus/compose.yaml` contiene un único servicio opcional llamado `objectstore`. Sus puertos se enlazan a `127.0.0.1`, no a todas las interfaces. La imagen predeterminada de MinIO está fijada a una versión que publica ARM64; cualquier actualización debe ser explícita mediante `MNEMOSYNE_OBJECTSTORE_IMAGE`.

Preparación única en Uranus:

```bash
cd ~/learning/andry-de-zoomcamp/infra/uranus
cp .env.example .env
nvim .env
```

Crear credenciales largas y únicas; nunca copiarlas a `CURRENT.md`, a un prompt ni a Git. Después, desde una estación local:

```bash
./mnemo remote up datalake
./mnemo remote tunnel datalake
```

Los puertos locales predeterminados son `9100` para S3 y `9101` para la consola. No añadir Caddy ni publicar el servicio en `0.0.0.0` para completar el curso.

## 12. Protocolo ante fallos

### `start` informa cambios locales

No hace pull ni stash automáticamente. Revisar:

```bash
git status --short --branch
git diff
```

Después cerrar correctamente con `./mnemo end` o decidir conscientemente qué archivos conservar.

### Git informa divergencia

No usar force-push ni `git reset --hard`. Crear una rama de rescate y pedir a la IA que compare los commits antes de integrar.

### No hay Internet

Usar `--offline`, continuar localmente y crear el checkpoint. Sincronizar cuando vuelva la red.

### `end` bloquea un archivo

Leer el nombre mostrado. Mover secretos o datos fuera del seguimiento, añadir solo un ejemplo sin credenciales y repetir. No desactivar la protección para “hacer que pase”.

### Una imagen no funciona en Uranus

Comprobar primero que publique `linux/arm64`. No forzar emulación como solución predeterminada; usar una imagen multi-arquitectura o ejecutar esa práctica localmente en x86_64.

## 13. Contrato para cualquier IA

Al comenzar una conversación nueva:

> Lee `AGENTS.md`, `CURRENT.md` y `git status --short --branch`. Respeta la arquitectura local-first. Explica el objetivo, ejecuta un paso pequeño, verifica el resultado y deja `CURRENT.md` listo para continuar. No recrees arca-pg, n8n ni 9router; no administres el PostgreSQL de CasaOS desde Compose; no expongas servicios ni secretos.

Una IA debe mostrar el plan antes de instalar paquetes, preservar cambios existentes, usar documentación oficial para herramientas actuales y pedir dirección ante una divergencia o conflicto real.

## 14. Definición de una sesión bien cerrada

La sesión termina únicamente cuando se cumplen estas condiciones:

- existe un resultado comprobado;
- las pruebas relevantes pasan;
- `CURRENT.md` contiene el próximo comando exacto;
- no hay secretos ni datasets en el checkpoint;
- existe un commit local;
- el push se completó o quedó anotado que falta sincronizar.

Con este contrato, cambiar de PC no exige recordar mentalmente el contexto: la siguiente estación reconstruye el entorno y lee el punto exacto de continuación.

## 15. Referencias técnicas oficiales

- Proyectos y sincronización con uv: <https://docs.astral.sh/uv/guides/projects/>
- Perfiles de Docker Compose: <https://docs.docker.com/compose/how-tos/profiles/>
- Selección aislada de configuración con `NVIM_APPNAME`: <https://neovim.io/doc/user/starting.html#%24NVIM_APPNAME>
- HOME independiente en Distrobox: <https://distrobox.it/useful_tips/>
- Etiquetas y arquitecturas de la imagen de MinIO: <https://hub.docker.com/r/minio/minio/tags>
- Errores no fast-forward en GitHub: <https://docs.github.com/en/get-started/using-git/dealing-with-non-fast-forward-errors>
