# Hyperfocus Roulette

Integración personalizada para Home Assistant que selecciona una próxima tarea según el tiempo disponible, la energía, la ubicación y las prioridades del usuario.

La idea nació como una automatización innecesaria y rápidamente se convirtió en otro proyecto del backlog.

> Estado: desarrollo experimental.

## Objetivo

Hyperfocus Roulette busca convertir proyectos grandes o difusos en microtareas concretas y elegir una que sea viable en el contexto actual.

Ejemplo:

> **ESPHome PC Power Control**  
> Dibujar únicamente la conexión entre el ESP-01, el BC548 y `PWR_SW`.  
> Tiempo estimado: 20 minutos.

La integración permitirá aceptar, omitir, completar o bloquear la tarea seleccionada.

## Estado actual

- Configuración desde la interfaz de Home Assistant.
- Una única instancia.
- Dispositivo virtual para agrupar entidades.
- Sensor de estado con valor `ready`.
- Traducción inicial al español.

Todavía no implementa tareas ni realiza sorteos.

## Instalación para desarrollo

El repositorio se encuentra en:

```text
/config/development/ha-hyperfocus-roulette/
```

La integración se enlaza con:

```bash
ln -s \
  /config/development/ha-hyperfocus-roulette/custom_components/hyperfocus_roulette \
  /config/custom_components/hyperfocus_roulette
```

Para validar y reiniciar:

```bash
ha core check
ha core restart
```

## Roadmap

### 0.1 — Esqueleto inicial

- [x] Crear la estructura de la integración.
- [x] Agregar el manifiesto.
- [x] Implementar el flujo de configuración.
- [x] Limitar la configuración a una instancia.
- [x] Crear un sensor con estado `ready`.
- [x] Agregar traducción al español.
- [x] Crear un dispositivo virtual.
- [x] Normalizar nombres de entidades.
- [x] Agregar pruebas básicas.

### 0.2 — Primera ruleta funcional

- [x] Crear `HyperfocusManager`.
- [x] Definir tres tareas temporales.
- [x] Crear el botón **Sortear**.
- [x] Mostrar la tarea seleccionada.
- [x] Evitar repeticiones inmediatas.
- [x] Disparar un evento al seleccionar una tarea.

### 0.3 — Ciclo de una tarea

- [x] Crear los botones **Aceptar**, **Omitir** y **Completar**.
- [x] Agregar estados: propuesta, activa, bloqueada y terminada.
- [x] Registrar el resultado de cada acción.
- [ ] Disparar eventos para automatizaciones.

### 0.4 — Persistencia

- [ ] Guardar proyectos y tareas.
- [ ] Restaurar el estado después de reiniciar.
- [ ] Permitir administrar proyectos.
- [ ] Permitir administrar tareas.
- [ ] Implementar migraciones de datos.

### 0.5 — Selección contextual

- [ ] Filtrar por tiempo disponible.
- [ ] Filtrar por energía.
- [ ] Filtrar por ubicación.
- [ ] Agregar modos **Avanzar** y **Estoy aburrido**.
- [ ] Implementar prioridades.
- [ ] Excluir tareas bloqueadas.

### 0.6 — Interfaz y distribución

- [ ] Crear una tarjeta con entidades nativas.
- [ ] Agregar opciones de configuración.
- [ ] Validar con Hassfest.
- [ ] Preparar instalación mediante HACS.
- [ ] Publicar la primera versión estable.

### Futuro innecesario pero maravilloso

- [ ] Estadísticas y logros.
- [ ] Anuncios sarcásticos.
- [ ] Cambios de iluminación según el proyecto.
- [ ] Temporizador de sesiones.
- [ ] Registro de “me fui por las ramas”.
- [ ] Tarjeta Lovelace personalizada.

## Licencia

Licencia pendiente de definir.