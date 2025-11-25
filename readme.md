---

# SRE Final Project – Flask App · Kubernetes · Prometheus · Grafana · Alertmanager

El objetivo del proyecto es implementar un entorno de monitoreo siguiendo prácticas de SER. Demostrando una solución funcional de monitoreo, métricas y alertas para una aplicación en producción. <img width="468" height="84" alt="image" src="https://github.com/user-attachments/assets/1332e581-640d-4361-895b-9679ab90d245" />

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
  * Latencia
  * Disponibilidad de la app

---

## **2. Kubernetes Deployment**

El proyecto incluye archivos.yaml que incluyen:

* Flask App (Deployment + Service)
* Prometheus
* Grafana
* Alertmanager
* ConfigMaps para reglas de alertas

Funciona en:

* Minikube
* Docker Desktop Kubernetes
* Cualquier cluster Kubernetes cloud (GKE/EKS/AKS)

---

## **3. Prometheus Integration**

Prometheus está configurado para:

* Scrappear métricas del Flask App
* Monitorear estado del sistema
* Cargar reglas de alertas desde ConfigMaps (incluyendo `sre-alerts.yml`)

Alertas implementadas:

* App Down
* High Error Rate
* Request Latency

---

## **4. Grafana Dashboards**

Grafana está desplegado a través de Kubernetes e incluye:

* Conexión a Prometheus
* Dashboards personalizados:

  * Tráfico por endpoint
  * Errores por minuto
  * Latencia promedio
  * Estado de pods

---

## **5. Alertmanager Deployment**

Alertmanager gestiona las alertas enviadas por Prometheus.

Configurado para:

* Agrupar alertas
* Manejar ruteo básico
* Visualización desde el UI
* (Opcional) envío a Slack/email si se activa bonus

---

## **6. Documentación**

Este repositorio contiene:

* `README.md` profesional
* Código organizado por carpetas
* Comentarios en configuraciones YAML
* Screenshots del stack funcionando
* `LICENSE.md`
* `CONTRIBUTING.md`

---

# Estructura del Proyecto 

```
project/
├── flask-app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── kubernetes/
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── prometheus-deployment.yaml
│   ├── grafana-deployment.yaml
│   ├── alertmanager-deployment.yaml
│   └── configmaps/
│       └── prometheus-rules.yaml
├── dashboards/
│   └── grafana-dashboard.json
├── screenshots/
│   ├── prometheus.png
│   ├── grafana.png
│   └── alerts.png
└── README.md
```

---

# Instrucciones para probar el Proyecto

> Instrucciones para que cualquiera pueda clonar y probar el proyecto.

### **1. Clonar el repositorio**

```bash
git clone https://github.com/<tu-usuario>/<tu-repo>.git
cd <tu-repo>
```

### **2. Iniciar Kubernetes**

```bash
minikube start
```

### **3. Construir imagen de Flask**

```bash
docker build -t sre-flask-app ./flask-app
```

### **4. Aplicar los manifiestos**

```bash
kubectl apply -f kubernetes/
```

### **5. Verificar estado de pods**

```bash
kubectl get pods -A
```

### **6. Acceder a Prometheus**

```bash
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
```

### **7. Acceder a Grafana**

```bash
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

Login:

```
admin
admin
```

### **8. Acceder a Alertmanager**

```bash
kubectl port-forward svc/alertmanager 9093:9093 -n monitoring
```

---

# Métricas

Este proyecto demuestra:

* Despliegue Kubernetes. 
* Implementación de observabilidad. 
* Creación de métricas personalizadas. 
* Manejo de alertas y monitoreo. 
  
---

