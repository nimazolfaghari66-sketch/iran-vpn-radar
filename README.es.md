<div align="center">

# 📡 Iran VPN Radar

**Descubrimiento, prueba y publicación automáticos de suscripciones VPN gratuitas para usuarios en Irán**

</div>

**Idiomas:** [فارسی (principal)](README.md) · [English](README.en.md) · [العربية](README.ar.md) · [中文](README.zh.md) · [Русский](README.ru.md) · **Español**

> ⚠️ **Traducción.** El idioma principal del proyecto es el persa ([README.md](README.md)). Este archivo es una traducción revisada.

---

## ⚠️ Estado de las pruebas en Irán

El proyecto tiene una regla inquebrantable: **una configuración solo se publica como «verificada en Irán» si fue probada realmente por una sonda situada físicamente en Irán.**

Hasta que haya una sonda conectada:

* todas las configuraciones permanecen en estado `PENDING_IRAN_TEST`;
* los archivos de suscripción publicados están **vacíos** a propósito;
* nunca se presenta un resultado extranjero o sintético como prueba iraní.

## ¿Qué es este proyecto?

Un sistema automatizado de código abierto que:

1. **Descubre** fuentes públicas de configuraciones VPN gratuitas.
2. **Extrae**, normaliza y **elimina duplicados**.
3. **Las prueba desde dentro de Irán** con clientes de protocolo reales.
4. **Elimina** las configuraciones rotas y duplicadas.
5. **Publica** archivos de suscripción por protocolo.
6. **Repite** el ciclo **cada 2 horas**.

## Protocolos compatibles

| Protocolo | Archivo de suscripción |
|-----------|------------------------|
| Todos | `subscriptions/all` |
| VLESS | `subscriptions/vless` |
| VMess | `subscriptions/vmess` |
| Trojan | `subscriptions/trojan` |
| Shadowsocks | `subscriptions/shadowsocks` |
| Hysteria2 | `subscriptions/hysteria2` |
| TUIC | `subscriptions/tuic` |
| SOCKS | `subscriptions/socks` |
| HTTP/HTTPS | `subscriptions/http` |

## Enlaces de suscripción

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic
```

Cada archivo tiene una variante Base64 con el sufijo `.b64`.

## Pruebas en Irán

La sonda debe ejecutarse en un host dentro de Irán:

```bash
export IRAN_PROBE_TOKEN="secreto-compartido-fuerte"
python3 probe/probe_agent.py --port 8787
```

Luego el motor central:

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="el-mismo-secreto"
```

Fases de la prueba: DNS, accesibilidad del servidor, handshake, túnel, internet a través del túnel, latencia, descarga limitada y estabilidad a corto plazo.

## Política de calidad

`DISCOVERED` → `PENDING_IRAN_TEST` → `TESTING` → `WORKING` / `DEGRADED` / `FAILED` / `EXPIRED` / `DUPLICATE`

Un fallo consecutivo: `DEGRADED` (se publica). Dos fallos: se elimina de la salida.

## Seguridad y privacidad

Todas las configuraciones son **públicas** y pueden ser inseguras o inestables. El proyecto nunca almacena ni publica contraseñas, tokens ni claves privadas. Ver [SECURITY.md](SECURITY.md).

## Contribuir

[CONTRIBUTING.md](CONTRIBUTING.md) — sugiere fuentes públicas, informa de configuraciones rotas, mejora el código, traduce la documentación.

## Licencia

[MIT](LICENSE)
