# Hyperfocus Roulette

Integración personalizada para Home Assistant que selecciona una próxima tarea según el tiempo disponible, la energía, la ubicación y las prioridades del usuario.

La idea nació como una automatización innecesaria y rápidamente se convirtió en otro proyecto del backlog.

> Estado: desarrollo experimental — versión 0.3 completada.

## Objetivo

Hyperfocus Roulette busca convertir proyectos grandes o difusos en microtareas concretas y elegir una que sea viable en el contexto actual.

Ejemplo:

> **ESPHome PC Power Control**  
> Dibujar únicamente la conexión entre el ESP-01, el BC548 y `PWR_SW`.  
> Tiempo estimado: 20 minutos.

La integración permite sortear, aceptar, omitir y completar una tarea. Una tarea se bloquea automáticamente después de tres omisiones consecutivas.

## Estado actual

- Configuración desde la interfaz de Home Assistant.
- Una única instancia.
- Dispositivo virtual para agrupar entidades.
- Tres tareas temporales almacenadas en memoria.
- Botones **Sortear**, **Aceptar**, **Omitir** y **Completar**.
- Sensor que muestra la tarea actual, su estado y cantidad de omisiones.
- Estados disponible, propuesta, activa, bloqueada y terminada.
- Bloqueo automático después de tres omisiones consecutivas.
- Exclusión de tareas bloqueadas y terminadas.
- Detección de que no quedan tareas disponibles.
- Registro temporal de los resultados de las acciones.
- Evento `hyperfocus_roulette_task_selected` al presentar una propuesta.
- Traducciones en inglés, español y español latinoamericano.
- Pruebas automáticas ejecutadas mediante GitHub Actions.

Los datos todavía se almacenan únicamente en memoria y se reinician al recargar Home Assistant.

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
- [x] Disparar el evento `hyperfocus_roulette_task_selected`.

### 0.3 — Ciclo de una tarea

- [x] Crear los botones **Aceptar**, **Omitir** y **Completar**.
- [x] Agregar estados: disponible, propuesta, activa, bloqueada y terminada.
- [x] Registrar omisiones consecutivas.
- [x] Bloquear una tarea después de tres omisiones.
- [x] Excluir tareas bloqueadas y terminadas de los sorteos.
- [x] Informar cuando no quedan tareas disponibles.
- [x] Registrar el resultado de cada acción.
- [x] Disparar el evento `hyperfocus_roulette_task_action`.

### 0.4 — Persistencia

- [x] Crear modelos separados para proyectos y tareas.
- [x] Asignar identificadores estables a los proyectos y las tareas.
- [x] Serializar proyectos, tareas, estado e historial.
- [x] Guardar los datos mediante `Store`.
- [x] Restaurar los datos después de reiniciar.
- [x] Crear los datos iniciales solamente en la primera instalación.
- [x] Guardar automáticamente después de cada acción.
- [ ] Permitir administrar proyectos.
- [ ] Permitir administrar tareas.
- [ ] Implementar migraciones de datos.
- [x] Agregar pruebas de persistencia y restauración.

### 0.5 — Selección contextual

- [ ] Filtrar por tiempo disponible.
- [ ] Filtrar por energía.
- [ ] Filtrar por ubicación.
- [ ] Agregar modos **Avanzar** y **Estoy aburrido**.
- [ ] Implementar prioridades.

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