---

# SRE Final Project – Flask App · Kubernetes · Prometheus · Grafana · Alertmanager

El objetivo del proyecto es implementar un entorno de monitoreo siguiendo prácticas de SER. Demostrando una solución funcional de monitoreo, métricas y alertas para una aplicación en producción. 

---

#  La Implementación Incluye

1.	La aplicación Flask que expone métricas. 
2.	Prometheus para recolectar métricas. 
3.	AlertManager para poder gestionar las tareas. 
4.	Grafana para visualización de dashboards. 
5.	Reglas Personalizadas de alertas (en ConfigMap). 
6.	Kubernetes como plataforma de despliegue. 

---

## **1. Desarrollo de la Aplicación – Flask App with Metrics**

* Aplicación construida con Flask.
* Endpoints que generan comportamientos distintos para poder monitorear.
* Exposición de métricas en `/metrics` (formato Prometheus).
* Métricas implementadas:

  * `http_requests_total`
  * `http_errors_total`
  * Métricas de latencia
  * Métricas personalizadas para la demo 
  * Docker file disponible en el raíz del proyecto 

---

## **2. Kubernetes Deployment**

Toda la configuración de Kubernetes está en /k8s.

Incluye:

* `Deployment.yaml`: Despliegue de la aplicación
* `Service.yaml`: Servicio para exponer la app
* `namespace.yaml`: Namespace dedicado (monitoring)
* `grafana-deployment.yaml`: Instalación de Grafana
* `prometheus-deployment.yaml`: Instalación de Prometheus
* `prometheus-configmap.yaml`: Configuración de Prometheus
* `prometheus-rules.yaml`: Reglas de alertas (ConfigMap)

---

## **3. Prometheus Integration**

Prometheus está configurado para:

* Scrappear métricas del Flask App
* Monitorear estado del sistema

ConfigMaps Personalizados: 

* `prometheus-configmap.yaml`
* `prometheus-rules.yaml`

Alertas implementadas:

* App Down
* High Error Rate
* Request Latency

---

## **4. Grafana Dashboards**

Grafana incluye (`grafana-deployment.yaml`):

* Conexión a Prometheus
* Dashboards personalizados:

  * Tráfico por endpoint
  * Errores por minuto
  * Latencia. 
  * Estado de pods

---

## **5. Alertmanager Deployment**

Alertmanager gestiona las alertas enviadas por Prometheus.

Alermanager se configura con: 

* `alermanager-config.yaml`
* `alertmanager-deployment.yaml`

Configurado para:

* Agrupar alertas
* Manejar ruteo básico
* Visualización desde el UI

---

## **6. Documentación**

Este repositorio contiene:

* `README.md` profesional
* Código organizado 
* Comentarios en configuraciones YAML
* Kubernetes dividido por componentes. 
* `LICENSE.md`
* `CONTRIBUTING.md`

---

# Estructura del Proyecto 

```
sre-flask-app/
├── app.py
├── Dockerfile
├── requirements.txt
├── alertmanager-config.yaml
├── alertmanager-deployment.yaml
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    ├── namespace.yaml
    ├── monitoring.yaml
    ├── grafana-deployment.yaml
    ├── prometheus-configmap.yaml
    ├── prometheus-deployment.yaml
    └── prometheus-rules.yaml

└── README.md
```

---

## Instrucciones del Proyecto

---

## Cómo probar el proyecto y ver métricas

Esta sección describe los pasos necesarios para verificar que la aplicación, Prometheus y Grafana están funcionando correctamente y que las métricas se están recolectando.

Los pasos asumen que ya aplicaste todos los manifests de Kubernetes (`k8s/`) y que Minikube (u otro cluster) está levantado.

---

### 1. Verificar que todos los pods están en **Running**

```bash
kubectl get pods -n sre-app
kubectl get pods -n monitoring
```
<img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/14e26a6d-8733-4884-9bd7-ccabc56b6640" />

> Si el pod de `sre-flask-app` está en `ImagePullBackOff`, es porque el cluster no encuentra la imagen.
> Solución (con Minikube):
>
> ```bash
> docker build -t sre-flask-app:latest .
> minikube image load sre-flask-app:latest
> kubectl rollout restart deployment sre-flask-app -n sre-app
> ```

---

### 2. Probar la aplicación Flask y sus métricas

#### 2.1. Hacer *port-forward* a la app

```bash
kubectl port-forward -n sre-app deployment/sre-flask-app 5001:5001
```
<img width="582" height="92" alt="image" src="https://github.com/user-attachments/assets/860d13f4-f10b-42ec-a997-2a658f239818" />

En otra terminal o en tu navegador:

* Home

  ```text
  http://localhost:5001/
  ```
* Healthcheck

  ```text
  http://localhost:5001/health
  ```
* Métricas

  ```text
  http://localhost:5001/metrics
  ```

Si `/metrics` muestra muchas líneas de texto con nombres como `http_requests_total`, la app está exponiendo métricas correctamente.

---

### 3. Generar tráfico para que haya datos que graficar

Desde otra terminal, ejecuta algunos requests:

```bash
# Home
curl http://localhost:5001/

# Health
curl http://localhost:5001/health

# Crear algunas órdenes
curl -X POST http://localhost:5001/order -H "Content-Type: application/json" \
  -d '{"item": "pizza", "quantity": 2}'

curl -X POST http://localhost:5001/order -H "Content-Type: application/json" \
  -d '{"item": "soda", "quantity": 1}'

# Listar órdenes
curl http://localhost:5001/orders

# Endpoint lento (latencia para pruebas)
curl http://localhost:5001/sometimes-slow

# Endpoint que siempre falla (para error rate)
curl http://localhost:5001/always-error
```

> Estos llamados hacen que suban las métricas:
>
> * `http_requests_total`
> * `http_errors_total`
> * `http_request_duration_seconds_*`
> * `orders_created_total`

---

### 4. Verificar métricas desde Prometheus

Para evitar conflictos de puertos locales, usamos el 9091 en máquina y el 9090 en el cluster:

```bash
kubectl port-forward -n monitoring svc/prometheus 9091:9090
```

Luego abre en el navegador:

```text
http://localhost:9091
```

1. Ve a **Status → Targets**
2. Verifica que ambos targets estén en **UP**:

   * `prometheus`
   * `sre-flask-app`

  <img width="2918" height="1054" alt="image" src="https://github.com/user-attachments/assets/3a90cf68-f5ed-436d-b5ea-b7d11cbc25f1" />

---

### 5. Conectar Grafana a Prometheus 

> Importante: Grafana y Prometheus corren **dentro del cluster**, por lo que NO deben usarse URLs con `localhost` entre ellos.

#### 5.1. Abrir Grafana

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

Navegador:

```text
http://localhost:3000
```

Login:

```text
user: admin
pass: admin
```

#### 5.2. Configurar el Data Source de Prometheus

1. Ir a **Connections → Data sources → Add data source**

2. Seleccionar **Prometheus**

3. Configurar:

   * **URL**

     ```text
     http://prometheus:9090
     ```
   * **Access / Connection type**

     * Seleccionar **Server** (no Browser)

4. Click en **Save & Test**

Debería aparecer:

<img width="2228" height="380" alt="image" src="https://github.com/user-attachments/assets/d632fe43-3f60-4b73-8609-e694833fab49" />

```text
Data source is working
```

> Si aparece un error con `localhost` o `no such host`, es porque se está usando la URL equivocada.
> El nombre correcto del Service en este cluster es `prometheus` en el namespace `monitoring`, por eso funciona `http://prometheus:9090` con acceso **Server**.

---

### 6. Importar el dashboard de la SRE Flask App

Con el Data Source funcionando:

1. Ir a **Dashboards → New → Import**
2. Pegar el JSON del dashboard incluido en este repositorio (`dashboards/sre-flask-app-dashboard.json`)
3. Seleccionar el data source de Prometheus cuando lo pida
4. Hacer clic en **Import**

Si todo está configurado correctamente, deberías ver:

* Requests por endpoint (`/`, `/health`, `/order`, `/orders`, `/sometimes-slow`, `/always-error`)
* Error rate alto en `/always-error`
* Latencia p95 más alta en `/sometimes-slow`
* El contador de `orders_created_total` aumentando después de usar `/order`

Estos gráficos son los que se utilizan como evidencia en los screenshots del proyecto.

---
<img width="2906" height="1406" alt="image" src="https://github.com/user-attachments/assets/4c562728-0c06-466d-b6bd-d407ccb7ca53" />

<img width="2222" height="1178" alt="image" src="https://github.com/user-attachments/assets/e4af3ad9-6075-4248-bb32-206de6331d78" />

---

# Cómo ver alertas en Alertmanager

Esta sección explica cómo abrir Alertmanager y cómo **forzar alertas** para que aparezcan en su interfaz. Las alertas ya están definidas y cargadas en Prometheus; solo necesitas activar sus condiciones.

---

## Abrir Alertmanager

Primero, haz *port-forward* al servicio de Alertmanager:

```bash
kubectl port-forward -n monitoring svc/alertmanager 9093:9093
```

Luego abre en tu navegador:

```
http://localhost:9093
```
---

### **Forzar la alerta SreFlaskAppDown (App fuera de servicio)**

Esta alerta se activa cuando la aplicación no está disponible por **más de 1 minuto** (debido al `for: 1m`).

1. Escala la app a 0 réplicas:

   ```bash
   kubectl scale deployment sre-flask-app -n sre-app --replicas=0
   ```

2. Revisa que ya no existan pods:

   ```bash
   kubectl get pods -n sre-app
   ```

3. Espera **60–70 segundos**.

4. Ahora revisa:

   * En Prometheus → *Alerts*
   * En Alertmanager → pantalla principal

   La alerta **SreFlaskAppDown** debería aparecer como *Firing*.

5. Cuando termines de probar, vuelve a levantar la app:

   ```bash
   kubectl scale deployment sre-flask-app -n sre-app --replicas=1
   ```

---

### **Forzar la alerta SreFlaskHighErrorRate (alto porcentaje de errores 5xx)**

Esta alerta se activa cuando el endpoint `/always-error` empieza a fallar consistentemente.

Ejecuta:

```bash
for i in {1..100}; do
  curl -s http://localhost:5001/always-error > /dev/null
done
```

Espera unos segundos, luego revisa:

* Prometheus → *Alerts*
* Alertmanager → UI

---

### **Forzar la alerta SreFlaskHighLatency (latencia alta)**

Ejecuta solicitudes repetidas al endpoint lento `/sometimes-slow`:

```bash
for i in {1..30}; do
  curl -s http://localhost:5001/sometimes-slow > /dev/null
done
```

Después de unos segundos:

* Verás la alerta **SreFlaskHighLatency** como activa en Prometheus y Alertmanager.

---
Alertas en Prometheus y Alert Manager App Down 

<img width="2876" height="1408" alt="image" src="https://github.com/user-attachments/assets/f0c79576-caff-4972-9528-e70c7346d412" />

<img width="2894" height="1180" alt="image" src="https://github.com/user-attachments/assets/d228d19f-1d50-45b7-b199-83506eae5dc7" />

<img width="2882" height="980" alt="image" src="https://github.com/user-attachments/assets/506d814a-ae53-4da4-bfa3-6d5c41d9026b" />

<img width="2272" height="288" alt="image" src="https://github.com/user-attachments/assets/0446f1dd-2df8-4323-9f12-5895cfeaac8d" />

# Metricas

Este proyecto demuestra:

* Dominio de Kubernetes
* Observabilidad moderna
* Monitoreo basado en métricas
* Alertas con Prometheus + Alertmanager
* Visualización profesional con Grafana
* Documentación clara y completa

---




