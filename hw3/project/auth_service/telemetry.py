import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

def setup_telemetry(app, service_name: str):
    # Resource attributes
    resource = Resource.create({"service.name": service_name})

    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Prometheus Metrics
    Instrumentator().instrument(app).expose(app)
