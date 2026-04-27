import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Modelador AWS para IA",
    layout="wide",
    page_icon="🏗️"
)

# ─────────────────────────────────────────────
# CASO BASE
# ─────────────────────────────────────────────
CASO_BASE = {
    "sector": "Asegurador",
    "documentos_diarios": 18000,
    "usuarios_simultaneos": 220,
    "latencia_max_seg": 4,
    "pii": True,
    "presupuesto": "Medio",
    "variabilidad_demanda": "Media",
    "preferencia_estrategica": "Gestionado",
    "disponibilidad_objetivo": "Alta",
}

# ─────────────────────────────────────────────
# REGLAS DE DECISIÓN
# ─────────────────────────────────────────────

def recomendar_inferencia(preferencia_estrategica):
    """Regla 4 y 5: inferencia según preferencia estratégica."""
    if preferencia_estrategica == "Gestionado":
        return "Amazon Bedrock — modelo gestionado, menor overhead operativo."
    return "Amazon SageMaker — control fino del modelo, mayor personalización."


def recomendar_seguridad(pii, presupuesto):
    """
    Regla 6 (reforzada): si hay PII, se añaden controles avanzados.
    Si además el presupuesto es Bajo, se prioriza minimización estricta
    sobre herramientas de terceros para no sobrecostear.
    """
    if pii:
        base = (
            "Controles reforzados: cifrado en tránsito y en reposo (KMS), "
            "minimización de datos en cada capa, revisión humana obligatoria "
            "en casos sensibles, políticas IAM de mínimo privilegio, "
            "auditoría con AWS CloudTrail y conformidad RGPD/LOPD."
        )
        if presupuesto == "Bajo":
            base += (
                " Dado el presupuesto ajustado, se priorizan controles nativos "
                "de AWS (IAM, KMS, CloudTrail) antes de soluciones de terceros."
            )
        return base
    return (
        "Controles estándar: IAM con mínimo privilegio, cifrado en reposo "
        "y monitoreo básico con CloudWatch."
    )


def recomendar_datos(documentos_diarios, pii):
    """Capa de datos adaptada al volumen y sensibilidad."""
    if documentos_diarios > 10000 and pii:
        return (
            "S3 con clasificación automática (Macie) para documentos sensibles. "
            "Particionado por fecha y tipo de siniestro. "
            "Ciclo de vida definido para retención y borrado."
        )
    if documentos_diarios > 10000:
        return (
            "S3 con particionado por fecha/tipo. "
            "Ingesta a través de AWS Glue para normalización documental."
        )
    return "S3 estándar con catálogo básico en AWS Glue."


def recomendar_integracion(latencia_max_seg, usuarios_simultaneos):
    """
    Regla 7 (reforzada): si la latencia es baja, se explicita
    preocupación por rendimiento y se añade caché.
    """
    partes = [
        "API Gateway + AWS Lambda para orquestación de flujos documentales."
    ]
    if latencia_max_seg <= 4:
        partes.append(
            f"⚠️ Latencia objetivo ≤{latencia_max_seg}s: se recomienda caché "
            "de respuestas frecuentes (ElastiCache/Redis) y optimización "
            "del pipeline de embeddings."
        )
    if usuarios_simultaneos > 100:
        partes.append(
            f"Con {usuarios_simultaneos} usuarios concurrentes, el diseño debe "
            "contemplar auto-scaling en Lambda y throttling en API Gateway."
        )
    return " ".join(partes)


def recomendar_observabilidad(variabilidad_demanda, presupuesto):
    """
    Regla 8 (reforzada): alta variabilidad → observabilidad + control de costes.
    Regla 10: presupuesto bajo → evitar sobredimensionamiento.
    """
    if variabilidad_demanda == "Alta":
        obs = (
            "CloudWatch con dashboards en tiempo real, alertas automáticas de coste "
            "(AWS Budgets + Cost Anomaly Detection), métricas de inferencia y "
            "rastreo distribuido con AWS X-Ray."
        )
    elif variabilidad_demanda == "Media":
        obs = (
            "Monitoreo continuo con CloudWatch Metrics y revisión semanal de consumo. "
            "Alertas sobre latencia p95 y tasa de error."
        )
    else:
        obs = "Observabilidad básica con CloudWatch Logs y revisión mensual de KPIs."

    if presupuesto == "Bajo":
        obs += (
            " FinOps: uso de Savings Plans y revisión mensual de recursos "
            "infrautilizados para evitar sobredimensionamiento."
        )
    return obs


def recomendar_aplicacion(disponibilidad_objetivo):
    """Regla 9: alta/muy alta disponibilidad → resiliencia explícita."""
    base = "Interfaz web interna para gestores y analistas (React o Streamlit interno)."
    if disponibilidad_objetivo in ("Alta", "Muy alta"):
        base += (
            f" Dado el objetivo '{disponibilidad_objetivo}', el despliegue debe "
            "contemplar multi-AZ, health checks y plan de recuperación ante fallos (RTO/RPO definidos)."
        )
    return base


def recomendar_tradeoff(preferencia_estrategica, pii, presupuesto):
    """Trade-off principal explícito y justificado."""
    if preferencia_estrategica == "Gestionado":
        tradeoff = (
            "**Velocidad de lanzamiento vs. control operativo.** "
            "Se elige Amazon Bedrock por su menor overhead de mantenimiento, "
            "asumiendo que la aseguradora prioriza llegar a producción rápido "
            "sobre tener control total del modelo subyacente."
        )
    else:
        tradeoff = (
            "**Control fino vs. velocidad de despliegue.** "
            "Se elige SageMaker para maximizar la personalización del modelo, "
            "asumiendo capacidad interna de MLOps. "
            "El coste operativo y el tiempo de despliegue serán mayores."
        )
    if pii and presupuesto == "Medio":
        tradeoff += (
            " La presencia de PII añade un segundo trade-off: "
            "**seguridad vs. rendimiento** — los controles de anonimización "
            "y revisión humana aumentan la latencia, por lo que el equipo "
            "debe fijar el umbral de escalado a gestor humano con cuidado."
        )
    return tradeoff


# ─────────────────────────────────────────────
# GENERADORES DE OUTPUT
# ─────────────────────────────────────────────

def generar_capas(datos):
    return {
        "1. Datos": recomendar_datos(
            datos["documentos_diarios"], datos["pii"]
        ),
        "2. Integración": recomendar_integracion(
            datos["latencia_max_seg"], datos["usuarios_simultaneos"]
        ),
        "3. Inferencia / Modelo": recomendar_inferencia(
            datos["preferencia_estrategica"]
        ),
        "4. Aplicación": recomendar_aplicacion(
            datos["disponibilidad_objetivo"]
        ),
        "5. Seguridad y Gobierno": recomendar_seguridad(
            datos["pii"], datos["presupuesto"]
        ),
        "6. Observabilidad y FinOps": recomendar_observabilidad(
            datos["variabilidad_demanda"], datos["presupuesto"]
        ),
    }


def generar_riesgos(datos):
    riesgos = [
        {
            "Riesgo": "Exposición de datos personales sensibles (PII)",
            "Mitigación": "Minimización en cada capa, revisión humana, cifrado KMS y auditoría CloudTrail.",
            "Rol responsable": "Compliance + CISO",
            "Acción inmediata": "Validar tratamiento de PII antes del despliegue.",
        },
        {
            "Riesgo": f"Latencia superior al objetivo (>{datos['latencia_max_seg']}s)",
            "Mitigación": "Caché de respuestas frecuentes, optimización de embeddings y pruebas de carga.",
            "Rol responsable": "Arquitecto SI/TI",
            "Acción inmediata": "Definir y ejecutar pruebas de rendimiento en staging.",
        },
        {
            "Riesgo": "Sobrecoste de inferencia por variabilidad de demanda",
            "Mitigación": "Alertas de consumo (AWS Budgets), revisión quincenal y Savings Plans.",
            "Rol responsable": "FinOps / Responsable de Operación",
            "Acción inmediata": "Establecer presupuesto mensual y umbral de alerta.",
        },
    ]
    return pd.DataFrame(riesgos)


def generar_slos(datos):
    # Mapeo de disponibilidad_objetivo a porcentaje SLA orientativo
    disponibilidad_map = {
        "Media": "99,5 %",
        "Alta": "99,9 %",
        "Muy alta": "99,99 %",
    }
    slos = [
        {
            "Indicador": "Latencia de respuesta (p95)",
            "Valor objetivo": f"≤ {datos['latencia_max_seg']} s",
            "Cómo medirlo": "CloudWatch Metric — API Gateway latency p95",
        },
        {
            "Indicador": "Disponibilidad del servicio",
            "Valor objetivo": disponibilidad_map.get(datos["disponibilidad_objetivo"], "—"),
            "Cómo medirlo": "CloudWatch Synthetics (canarios) + health checks",
        },
        {
            "Indicador": "Tasa de escalado a gestor humano",
            "Valor objetivo": "< 15 % de consultas",
            "Cómo medirlo": "Métrica personalizada en CloudWatch desde la lógica de la app",
        },
    ]
    return pd.DataFrame(slos)


# ─────────────────────────────────────────────
# SIDEBAR — INPUTS
# ─────────────────────────────────────────────

st.sidebar.header("⚙️ Parámetros del caso")
st.sidebar.caption("Caso base: Aseguradora — área de siniestros")

sector = st.sidebar.text_input("Sector", CASO_BASE["sector"])
documentos_diarios = st.sidebar.number_input(
    "Documentos diarios", min_value=0, value=CASO_BASE["documentos_diarios"]
)
usuarios_simultaneos = st.sidebar.number_input(
    "Usuarios simultáneos", min_value=0, value=CASO_BASE["usuarios_simultaneos"]
)
latencia_max_seg = st.sidebar.number_input(
    "Latencia máxima (s)", min_value=1, value=CASO_BASE["latencia_max_seg"]
)
pii = st.sidebar.checkbox(
    "¿Hay datos personales sensibles (PII)?", value=CASO_BASE["pii"]
)
presupuesto = st.sidebar.selectbox(
    "Presupuesto", ["Bajo", "Medio", "Alto"], index=1
)
variabilidad_demanda = st.sidebar.selectbox(
    "Variabilidad de la demanda", ["Baja", "Media", "Alta"], index=1
)
preferencia_estrategica = st.sidebar.selectbox(
    "Preferencia estratégica", ["Gestionado", "Control fino"], index=0
)
disponibilidad_objetivo = st.sidebar.selectbox(
    "Disponibilidad objetivo", ["Media", "Alta", "Muy alta"], index=1
)

datos = {
    "sector": sector,
    "documentos_diarios": documentos_diarios,
    "usuarios_simultaneos": usuarios_simultaneos,
    "latencia_max_seg": latencia_max_seg,
    "pii": pii,
    "presupuesto": presupuesto,
    "variabilidad_demanda": variabilidad_demanda,
    "preferencia_estrategica": preferencia_estrategica,
    "disponibilidad_objetivo": disponibilidad_objetivo,
}

# ─────────────────────────────────────────────
# MAIN — OUTPUT EJECUTIVO
# ─────────────────────────────────────────────

st.title("🏗️ Modelador de Arquitecturas AWS para IA")

st.divider()

# ── 1. RESUMEN EJECUTIVO ──────────────────────
st.subheader("📋 1. Resumen ejecutivo")

modo = "simplicidad operativa y velocidad de lanzamiento" \
    if datos["preferencia_estrategica"] == "Gestionado" \
    else "control fino del modelo y personalización"

pii_nota = (
    " La presencia de PII eleva el nivel de exigencia en seguridad y cumplimiento normativo."
    if datos["pii"] else ""
)

st.info(
    f"**Sector:** {datos['sector']}  \n"
    f"**Problema operativo:** Asistente interno para el área de siniestros — búsqueda documental, "
    f"borradores de respuesta y apoyo a gestores humanos.  \n"
    f"**Criterio dominante:** {modo.capitalize()}, con restricciones de latencia "
    f"(≤{datos['latencia_max_seg']} s), presupuesto {datos['presupuesto'].lower()} "
    f"y disponibilidad {datos['disponibilidad_objetivo'].lower()}.{pii_nota}"
)

st.divider()

# ── 2. ARQUITECTURA POR CAPAS ─────────────────
st.subheader("🗂️ 2. Arquitectura propuesta por capas")

capas = generar_capas(datos)
iconos = ["🗄️", "🔗", "🤖", "💻", "🔒", "📊"]
for (capa, descripcion), icono in zip(capas.items(), iconos):
    with st.expander(f"{icono} {capa}", expanded=True):
        st.write(descripcion)

st.divider()

# ── 3. TRADE-OFF PRINCIPAL ────────────────────
st.subheader("⚖️ 3. Trade-off principal")
st.warning(recomendar_tradeoff(
    datos["preferencia_estrategica"],
    datos["pii"],
    datos["presupuesto"]
))

st.divider()

# ── 4. MATRIZ RAGA ────────────────────────────
st.subheader("🚦 4. Matriz RAGA — Riesgos, Alternativas, Gobernanza y Acciones")
st.dataframe(generar_riesgos(datos), use_container_width=True, hide_index=True)

st.divider()

# ── 5. SLO / SLA ──────────────────────────────
st.subheader("📏 5. SLO / SLA propuestos")
st.dataframe(generar_slos(datos), use_container_width=True, hide_index=True)

st.divider()

# ── 6. REFLEXIÓN DEL EQUIPO ───────────────────
st.subheader("💬 6. Reflexión del equipo")
st.success(
    "**Decisión principal:** Se adopta Amazon Bedrock como motor de inferencia "
    "por la preferencia estratégica 'Gestionado', priorizando velocidad de despliegue "
    "y menor carga operativa sobre control total del modelo.  \n\n"
    "**Trade-off aceptado:** Se asume menor personalización del modelo a cambio de "
    "mayor agilidad operativa y reducción del overhead de MLOps.  \n\n"
    "**Riesgo crítico:** La presencia de PII obliga a controles estrictos que pueden "
    "aumentar la latencia percibida. El equipo deberá calibrar el umbral de escalado "
    "a gestor humano para no degradar la experiencia.  \n\n"
    "**Mejora para la siguiente iteración:** Validar con pruebas de carga reales "
    "si la latencia p95 se mantiene ≤4 s con los controles de seguridad activos, "
    "y explorar si la variabilidad media justifica activar auto-scaling proactivo."
)