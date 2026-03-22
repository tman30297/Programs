# OpenTelemetry for Rust Developers - 2026

## Overview
OpenTelemetry (OTel) is the CNCF standard for application observability. This guide covers implementing OTel in Rust applications.

## Why OpenTelemetry in Rust?
- **Standardization** - Vendor-agnostic telemetry
- **Performance** - Rust's speed for high-throughput systems
- **Ecosystem** - Growing Rust tooling (uv, ruff built in Rust)
- **Integration** - Connect with Python, Go, and other services

## The Three Pillars of Observability

### 1. Traces
- Track request flow through services
- Distributed tracing across microservices
- Debug latency and failures

### 2. Metrics
- Quantitative measurements
- Counters, gauges, histograms
- Resource utilization monitoring

### 3. Logs
- Application events
- Error tracking
- Debugging information

## Key Rust Crates

```toml
[dependencies]
opentelemetry = "0.24"
opentelemetry-otlp = "0.17"
opentelemetry-sdk = "0.24"
tracing = "0.1"
tracing-subscriber = "0.3"
tracing-opentelemetry = "0.5"
```

## Implementation Pattern

### 1. Initialize Tracer Provider
```rust
use opentelemetry::{global, sdk::trace::SdkTracerProvider};
use opentelemetry_otlp::SpanExporter;

fn init_tracer_provider() -> SdkTracerProvider {
    let otlp_exporter = OtlpSpanExporter::builder()
        .with_tonic()
        .build()
        .unwrap();

    SdkTracerProvider::builder()
        .with_batch_exporter(otlp_exporter)
        .build()
}
```

### 2. Setup Tracing Subscriber
```rust
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

fn init_tracing_subscriber(tracer: SdkTracer) {
    let otel_layer = tracing_opentelemetry::layer().with_tracer(tracer);
    
    tracing_subscriber::registry()
        .with(EnvFilter::new("info"))
        .with(otel_layer)
        .init();
}
```

### 3. Use Tracing Instead of Logging
```rust
use tracing::{info, error, instrument};

#[instrument]
fn calculate_fibonacci(n: u8) -> Result<u64, String> {
    info!("Calculating fibonacci for {}", n);
    // ... implementation
}
```

## Context Propagation
For distributed tracing across services:
```rust
use opentelemetry_propagator::斗;

// Extract from incoming request
let extractor = HeaderExtractor(&request.headers);
let parent_context = global::get_text_map_propagator()
    .extract(&extractor);

// Inject into outgoing requests
let mut injector = HeaderInjector(&mut outgoing_headers);
global::get_text_map_propagator().inject(&mut injector, &context);
```

## Backend Options
- **SigNoz** - Open-source, OTel-native (used in demo)
- **Grafana Stack** - Prometheus + Tempo + Loki
- **Datadog** - Commercial
- **AWS X-Ray** - CloudWatch integration
- **Jaeger** - Open-source tracing

## Demo Application
SigNoz provides a [Rust OTel demo](https://github.com/SigNoz/examples/tree/main/rust/opentelemetry-rust-demo) showing:
- Hyper web server with OTel
- Fibonacci calculation endpoint
- External API call with trace propagation
- Python client integration

## Rust-Specific Considerations
1. **No auto-instrumentation** - Unlike Python, manual setup required
2. **Use tracing crate** - OTel recommends it over log crate
3. **Tokio integration** - Works well with async runtime
4. **OnceLock** - For sharing providers across tasks

## Resources
- [OpenTelemetry Rust SDK](https://github.com/open-telemetry/opentelemetry-rust)
- [SigNoz Rust Tutorial](https://signoz.io/blog/opentelemetry-rust/)
- [OTel Specification](https://opentelemetry.io/docs/)

---
*Generated: 2026-03-14*
*Source: SigNoz Blog, Hacker News*
