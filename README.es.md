<div align="center">

# 📡 Iran VPN Radar

**Suscripciones VPN gratuitas, probadas desde dentro de Irán — se actualizan automáticamente cada 2 horas**

</div>

**Idiomas:** [فارسی (principal)](README.md) · [English](README.en.md) · [العربية](README.ar.md) · [中文](README.zh.md) · [Русский](README.ru.md) · **Español**

> ⚠️ **Traducción.** El idioma principal del proyecto es el persa ([README.md](README.md)).

<!-- radar:subscriptions:start -->
## 📥 Enlaces de suscripción

Copia un enlace y añádelo a tu cliente VPN. Eso es todo.

**Todos los protocolos (all):** [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all)

| Protocolo | Enlace de suscripción | Configuraciones activas |
|---|---|---|
| **VLESS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless) | 72 |
| **VMess** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess) | 1 |
| **Trojan** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan) | 72 |
| **Shadowsocks** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks) | 8 |
| **Hysteria2** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2) | 0 |
| **TUIC** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic) | 0 |
| **SOCKS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks) | 3 |
| **HTTP** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http) | 2 |

> Cada archivo tiene una variante Base64 con el sufijo `.b64`.

> Estos enlaces son del nivel «prioridad Irán»: se estableció un túnel real y hay evidencia de accesibilidad desde una red iraní, pero no están verificados desde dentro de Irán.
<!-- radar:subscriptions:end -->

### Cómo usar

1. Copia el enlace del protocolo que quieras de la tabla de arriba.
2. En tu cliente, elige **Añadir suscripción (Add subscription)**.
3. Pega el enlace y actualiza.
4. Elige un servidor y conéctate.

## 📊 Estado

* **Actualización:** automática, cada 2 horas.
* **Último estado:** [status/summary.json](status/summary.json)

> ⚠️ **Nota:** solo se publican las configuraciones que superan una prueba real
> desde dentro de Irán. Hasta que una configuración supere esa prueba, los
> archivos permanecen vacíos. Nunca marcamos como funcional una configuración
> sin probar.

## 📈 Estado por protocolo

Los recuentos se actualizan cada 2 horas. **Saludables** significa que se estableció un túnel real. El objetivo es **100** configuraciones saludables por protocolo, contadas por separado.

| Protocolo | Descubiertas | Probadas | Túneles OK | Saludables | Objetivo | Déficit | Prioridad Irán | Suscripción |
|---|---|---|---|---|---|---|---|---|
| **vless** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vless&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vless&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vless&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vless&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vless&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vless&color=yellowgreen) | [`subscriptions/candidates/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vless) |
| **vmess** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vmess&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vmess&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vmess&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vmess&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vmess&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vmess&color=yellowgreen) | [`subscriptions/candidates/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vmess) |
| **trojan** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.trojan&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.trojan&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.trojan&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.trojan&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.trojan&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.trojan&color=yellowgreen) | [`subscriptions/candidates/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/trojan) |
| **shadowsocks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.shadowsocks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.shadowsocks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.shadowsocks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.shadowsocks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.shadowsocks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.shadowsocks&color=yellowgreen) | [`subscriptions/candidates/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/shadowsocks) |
| **hysteria2** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.hysteria2&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.hysteria2&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.hysteria2&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.hysteria2&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.hysteria2&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.hysteria2&color=yellowgreen) | [`subscriptions/candidates/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/hysteria2) |
| **tuic** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.tuic&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.tuic&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.tuic&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.tuic&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.tuic&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.tuic&color=yellowgreen) | [`subscriptions/candidates/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/tuic) |
| **socks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.socks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.socks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.socks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.socks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.socks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.socks&color=yellowgreen) | [`subscriptions/candidates/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/socks) |
| **http** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.http&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.http&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.http&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.http&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.http&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.http&color=yellowgreen) | [`subscriptions/candidates/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/http) |

## 🧪 Grupo de candidatas (no verificado desde Irán)

Un segundo grupo, claramente separado, contiene configuraciones cuyo túnel fue
establecido realmente por un cliente real (sing-box) — pero desde nuestro host
del motor, que **no está dentro de Irán**. Se ordenan de modo que las entradas
que una sonda iraní ya observó como accesibles aparecen primero.

* Todas las candidatas: [`subscriptions/candidates/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/all)
* Por protocolo: `subscriptions/candidates/vless`, `.../vmess`, `.../trojan`,
  `.../shadowsocks`, `.../hysteria2`, `.../tuic`, `.../socks`, `.../http`

> Estas **no** están verificadas desde Irán y pueden estar bloqueadas dentro de
> Irán. Úsalas solo como alternativa o punto de partida. Los archivos de arriba
> (sin `/candidates/`) son los verificados desde Irán.

## 📱 Clientes compatibles

v2rayNG · v2rayN · sing-box · Hiddify / NekoBox · Clash / Clash.Meta

## ❓ Preguntas frecuentes

**¿Con qué frecuencia se actualizan las suscripciones?** Cada 2 horas, automáticamente.

**¿Por qué los archivos están vacíos?** Porque ninguna configuración ha superado
aún la prueba «verificada desde dentro de Irán». Es deliberado, para no publicar
configuraciones rotas.

**¿Cómo reporto una configuración rota?** Abre un
[Issue](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/issues).
Nunca publiques contraseñas, enlaces personales ni información privada.

**¿Son seguras estas configuraciones?** Las configuraciones son **públicas** y
pueden ser inestables o pertenecer a otra persona. Úsalas bajo tu propio riesgo.
Ver [SECURITY.md](SECURITY.md).
