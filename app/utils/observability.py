import logging
# --- OpenTelemetry core ---
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource

# --- Tracing ---
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# --- Metrics ---
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# --- Logs ---
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider, get_logger_provider

# --- Instrumentation ---
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


class OTLPFormatter(logging.Formatter):
    def format(self, record):
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            trace_id = format(ctx.trace_id, '032x')
            span_id = format(ctx.span_id, '016x')
            record.msg = f"[trace_id={trace_id} span_id={span_id}] {record.msg}"
        return super().format(record)


class Observability():
    def __init__(self):
        self.__resource = Resource(attributes={
            "service.name": "sample_pr"
        })

        self.__endpoint = "http://XXXXXXXXXXXXXXXXXXXXXXXXX.elb.ap-northeast-1.amazonaws.com:4317"

        self.__init_logging()
        self.__init_trace()
        self.__init_metrics()


    def __init_logging(self):
        log_exporter = OTLPLogExporter(endpoint=self.__endpoint, insecure=True)
        log_processor = BatchLogRecordProcessor(log_exporter)
        logger_provider = LoggerProvider(resource=self.__resource)
        logger_provider.add_log_record_processor(log_processor)
        set_logger_provider(logger_provider)

        # Python 標準ログを OTel ロガー経由にする
        handler = LoggingHandler(level=logging.INFO)
        handler.setFormatter(OTLPFormatter())
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    def __init_trace(self):
        trace.set_tracer_provider(TracerProvider(resource=self.__resource))
        self.__tracer = trace.get_tracer(__name__)
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=self.__endpoint, insecure=True)
        )
        trace.get_tracer_provider().add_span_processor(span_processor)

    def __init_metrics(self):
        metrics.set_meter_provider(
            MeterProvider(
                resource=self.__resource,
                metric_readers=[
                    PeriodicExportingMetricReader(
                        OTLPMetricExporter(endpoint=self.__endpoint, insecure=True),
                        export_interval_millis=5000
                    )
                ]
            )
        )
        meter = metrics.get_meter(__name__)
        self.__request_counter = meter.create_counter(
            name="custom.request.count",
            unit="1",
            description="Number of requests"
        )
        self.__response_histogram = meter.create_histogram(
            name="custom.response.duration",
            unit="ms",
            description="Response duration in milliseconds"
        )

    @property
    def request_counter(self):
        return self.__request_counter

    @property
    def response_histogram(self):
        return self.__response_histogram

    @property
    def tracer(self):
        return self.__tracer
