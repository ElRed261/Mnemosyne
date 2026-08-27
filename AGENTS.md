# Mnemosyne — contrato para agentes de IA

## Misión

Ayudar a Andry a completar Data Engineering Zoomcamp mediante explicaciones textuales, práctica verificable y continuidad entre dispositivos. Preparar el entorno y ejecutar el siguiente paso pequeño; no convertir cada sesión en un rediseño de infraestructura.

## Arquitectura vinculante

La estrategia es **local-first**:

- Git privado es la memoria y fuente de verdad.
- PCrda es el nodo x86_64 principal y soporta cargas pesadas.
- La laptop es el nodo móvil x86_64.
- `tecnologia04` es un nodo local autorizado de INDOMET; mantener el proyecto aislado y sin datos institucionales.
- Uranus (`uranus-core-vnic`, Ubuntu ARM64) es staging para pruebas semirreales y servicios puntuales. El estudio diario no puede depender de su disponibilidad ni de una conexión rápida.

`arca-pg`, `n8n` y `9router` fueron eliminados. No recrearlos. PostgreSQL será instalado desde CasaOS y debe considerarse servicio externo administrado: no detenerlo, borrarlo ni declararlo en el Compose de Mnemosyne.

## Fuente de continuidad

Leer en este orden:

1. `AGENTS.md`;
2. `CURRENT.md`;
3. `git status --short --branch`;
4. la documentación del módulo activo;
5. las pruebas y evidencia más recientes.

El ciclo obligatorio es:

> objetivo pequeño → ejecución → verificación → evidencia → CURRENT.md → commit → push cuando haya red

Si no hay Internet, permitir commit local y continuar. No bloquear la sesión por no poder llegar a GitHub o Uranus.

## Automatización

Usar `./mnemo` como interfaz estable:

```bash
./mnemo doctor
./mnemo onboard PCrda --apply
./mnemo bootstrap --profile workstation
./mnemo start
./mnemo current
./mnemo end
./mnemo sync
./mnemo edit
./mnemo remote status
```

En un nodo nuevo, `onboard` combina instalación, registro del dispositivo, sincronización y reconstrucción del entorno. Sustituir `PCrda` por `laptop`, `tecnologia04` o `Uranus`.

Antes de cambiar `scripts/mnemo.py`, explicar el contrato que se modifica y ejecutar las pruebas. Mantener el CLI con biblioteca estándar para que pueda arrancar antes de instalar `uv`.

## Política de instalación

- Mostrar un plan antes de instalar paquetes; usar `--apply` para ejecutar.
- No reemplazar una instalación Docker existente que funciona.
- No añadir el usuario al grupo Docker ni habilitar servicios sin confirmación.
- Usar repositorios oficiales de la distribución o del proveedor.
- Fijar Python 3.12 con `uv`; sincronizar mediante `uv.lock`.
- Mantener compatibilidad con bash y fish; no depender de activar `.venv`.

## Neovim

Usar `NVIM_APPNAME=mnemosyne-nvim` y la configuración aislada de `tools/nvim/init.lua`. No escribir en `~/.config/nvim`. Introducir un comando o movimiento nuevo por sesión; evitar convertir plugins en un proyecto paralelo.

## Uranus

- Consultar puertos antes de desplegar.
- Mantener servicios de práctica en `127.0.0.1` y acceder por SSH/Tailscale.
- No modificar Caddy ni publicar puertos en `0.0.0.0` por defecto.
- Operar únicamente `infra/uranus/compose.yaml` desde `./mnemo remote`.
- No ejecutar `docker compose down -v` ni borrar volúmenes automáticamente.
- Verificar compatibilidad ARM64 de cada imagen.
- No asumir que existe una cuenta AWS/GCP; usar staging local hasta que el curso exija nube real.

## Datos y secretos

Nunca versionar:

- `.env` y credenciales;
- claves SSH, PEM o JSON de cuentas de servicio;
- `.venv`, cachés o descargas;
- datos brutos o datasets grandes;
- bases SQLite/PostgreSQL y volúmenes Docker;
- `.terraform/`, `terraform.tfstate` o `*.tfvars` reales.

No copiar información de INDOMET al repositorio personal, a Uranus ni a servicios externos.

## Git seguro

- Usar fast-forward para actualizar `main`.
- No hacer stash automático.
- No usar force-push, `git reset --hard` ni reescribir historial como solución automática.
- Ante divergencia, crear una rama de rescate y explicar el conflicto.
- Revisar archivos y secretos antes de preparar un checkpoint.

## Formato pedagógico

No depender de videos. Para cada tarea entregar:

1. objetivo;
2. explicación conceptual breve;
3. comando exacto;
4. resultado esperado;
5. comprobación;
6. diagnóstico de fallos;
7. evidencia que debe conservarse;
8. siguiente acción concreta.

Los videos son únicamente material de rescate si una demostración visual concreta resulta necesaria.
