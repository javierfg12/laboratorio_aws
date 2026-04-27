# Modelador de Arquitecturas AWS para IA
### M4_S25A — Diseño de Sistemas · José Fernández Tamames

---

## Descripción

Aplicación Streamlit que actúa como recomendador arquitectónico mínimo.
Traduce variables de negocio y técnicas de un caso empresarial (aseguradora —
área de siniestros) a una propuesta lógica de integración para IA en AWS.

---

## Estructura del proyecto

```
laboratorio_aws_ia/
├── app.py            # Aplicación principal (MVP)
├── requirements.txt  # Dependencias
└── README.md         # Este fichero
```

---

## Cómo ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Caso base

| Variable | Valor |
|---|---|
| Sector | Asegurador |
| Documentos diarios | 18.000 |
| Usuarios simultáneos | 220 |
| Latencia objetivo | ≤ 4 s |
| PII | Sí |
| Presupuesto | Medio |
| Variabilidad de demanda | Media |
| Preferencia estratégica | Gestionado |
| Disponibilidad objetivo | Alta |

---

## Decisiones del equipo

- **Motor de inferencia:** Amazon Bedrock (preferencia "Gestionado")
- **Trade-off aceptado:** Velocidad de lanzamiento vs. control fino del modelo
- **Riesgo crítico:** PII + latencia — los controles de seguridad pueden incrementar la latencia p95
- **Mejora propuesta:** Pruebas de carga reales con controles activos para validar el SLO de latencia

---

## Nota sobre uso de IA

La IA se usó como asistente para estructurar el código base y revisar reglas.
Las decisiones de diseño (trade-off, arquitectura, justificación) son del equipo.
