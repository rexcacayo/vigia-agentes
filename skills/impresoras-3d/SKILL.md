---
name: impresoras-3d
description: Qué se puede leer y tocar en marcha en cada impresora 3D a través de su API local (Flashforge, Anycubic, Klipper/Moonraker y otras), y cómo razonar cuando llega un modelo nuevo. Úsala antes de proponer cualquier ajuste en caliente.
---

# Impresoras 3D: capacidades por API

El vigía habla con cada impresora mediante un **adaptador** (`vigia/impresoras/<tipo>.py`
en el repo `vigia_3d`). Cada adaptador declara un conjunto de **capacidades**: solo esas
acciones existen para esa máquina. Esta skill está pensada para crecer: cada impresora
nueva añade su sección.

## Contrato común (para cualquier modelo)

Toda máquina entrega un `maquina.json` con:
- `nombre`, `descripcion` (cámara, cinemática, qué no se puede cambiar)
- `capacidades`: subconjunto de
  `velocidad`, `flujo`, `temp_boquilla`, `temp_cama`, `z_offset`, `ventilador`,
  `pausar`, `reanudar`, `luz`
- `solo_con_permiso`: capacidades que nunca se aplican sin confirmación humana

Reglas:
1. **Propón ajustes en marcha solo dentro de `capacidades`.** Lo demás va como
   recomendación de perfil para la próxima impresión.
2. Los límites de seguridad (rangos por material, máximo de cambios, reversión) los
   aplica el código del vigía; tú propones y explicas.
3. Si un parámetro clave no se puede tocar en esta máquina pero sí en otra familia
   (p. ej. flujo o pressure advance con Klipper), dilo como «mejora posible del adaptador».

## Familias conocidas

### Flashforge Adventurer 5M / 5M Pro (firmware de serie) · adaptador `flashforge`
- API HTTP 8898 (`/detail`, `/control`), vídeo MJPEG 8080 (un solo espectador).
- En marcha: velocidad global %, temperaturas boquilla/cama, Z offset (capas 1–3),
  ventilador (con permiso), pausar/reanudar, luz.
- No: flujo, retracción, pressure advance, aceleraciones.

### Anycubic Kobra 3 / 3 Max / S1 (firmware de serie, modo LAN) · adaptador `anycubic`
- MQTT con TLS en la impresora (9883), credenciales por apretón de manos HTTP (18910),
  vídeo HTTP-FLV 18088.
- En marcha: pausar/reanudar, luz. Implementado y pendiente de validar: temperaturas,
  ventilador, modo de velocidad (silencioso/estándar/deportivo, no %).
- No: G-code libre, flujo, retracción, Z offset.
- Riesgo propio: impresiones largas en máquina grande → **falta de filamento**.

### Klipper + Moonraker (Creality K1, Qidi, Voron, AD5M con Forge-X/ZMod…) · adaptador `klipper` (pendiente)
- API REST 7125 y **G-code en caliente**: `M220` velocidad, `M221` flujo,
  `SET_PRESSURE_ADVANCE`, `SET_RETRACTION`, aceleraciones, `SET_GCODE_OFFSET`.
- Es la familia con más margen de corrección en marcha.

## Cuando llega una impresora nueva
1. Identifica su API local (documentación oficial o proyectos de la comunidad).
2. Lista qué se puede **leer** (estado, capa, temperaturas, cámara) y qué se puede **tocar**.
3. Declara solo capacidades **probadas** en la máquina; el resto, «pendiente».
4. Añade aquí su sección con el mismo formato.
