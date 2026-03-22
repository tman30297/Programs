# Additional Research Topics - March 2026

## Topics Researched
1. **Graph Databases** - Modern data relationship handling
2. **Serverless Computing** - Cloud-native architecture
3. **Internet of Things (IoT)** - Connected device ecosystems

---

## 1. Graph Databases

### Overview
Graph databases use graph structures (nodes, edges, properties) to represent and store data. They're a category of NoSQL database optimized for handling complex relationships.

### Key Concepts

**Nodes** - Entities like people, businesses, accounts
**Edges (Relationships)** - Connections between nodes, can be directed or undirected
**Properties** - Key-value pairs associated with nodes

### Types of Graph Models

1. **Labeled-Property Graph**
   - Nodes with labels and properties
   - Relationships have direction and can have properties
   - Examples: Neo4j, Titan

2. **Resource Description Framework (RDF)**
   - Each piece of info is a triple (subject-predicate-object)
   - Used for semantic web, linked data
   - Example: SPARQL endpoints

### Popular Graph Databases

| Database | Type | Notes |
|----------|------|-------|
| Neo4j | Property Graph | Most popular, ACID compliant |
| Amazon Neptune | Multi-model | Supports RDF and property graphs |
| ArangoDB | Multi-model | Document + graph + key-value |
| OrientDB | Multi-model | First multi-model DB |
| Neo4j AuraDB | Cloud | Managed Neo4j service |

### Use Cases
- **Social networks** - Friend recommendations, relationship tracking
- **Fraud detection** - Identifying suspicious patterns
- **Recommendation engines** - Product/content recommendations
- **Network/IT operations** - Infrastructure mapping
- **Knowledge graphs** - Semantic search

### Query Languages
- **Cypher** - Neo4j's declarative language
- **Gremlin** - Apache TinkerPop's graph traversal
- **SPARQL** - RDF query language
- **GQL** - New ISO standard (2020s)

### When to Use Graph DB
✓ Heavily interconnected data
✓ Need fast relationship queries
✓ Building recommendation systems
✓ Complex network analysis

### When NOT to Use
✗ Simple CRUD with few relationships
✗ Need strict schema
✗ Bulk analytics (use graph compute engines)

---

## 2. Serverless Computing

### Overview
Serverless computing is a cloud execution model where the cloud provider dynamically manages server allocation and provisioning. Despite the name, servers are still involved - developers just don't manage them.

### Key Characteristics
- **Pay-per-use** - Only pay for compute time consumed
- **Auto-scaling** - Automatic scaling to zero or high loads
- **No server management** - Infrastructure abstracted away
- **Event-driven** - Functions triggered by events

### Major Providers & Services

| Provider | FaaS Service | Notes |
|----------|--------------|-------|
| AWS | Lambda | Pioneer, most mature |
| Azure | Azure Functions | Good Microsoft integration |
| Google | Cloud Functions | Also Cloud Run for containers |
| IBM | Cloud Functions | OpenWhisk-based |
| Oracle | Fn | Open source framework |

### Serverless vs Traditional

| Aspect | Traditional | Serverless |
|--------|-------------|------------|
| Scaling | Manual/Configured | Automatic |
| Pricing | Hourly/monthly | Per-invocation |
| Cold starts | N/A | Potential latency |
| Control | Full server control | Limited |

### Common Use Cases
- **API backends** - REST/GraphQL endpoints
- **Data processing** - Image resizing, format conversion
- **Scheduled tasks** - Cron jobs, batch processing
- **Real-time file processing** - Upload triggers
- **IoT backends** - Device data ingestion
- **Chatbots** - Event-driven responses

### Challenges & Anti-Patterns

1. **Cold Starts** - Initial invocation latency
2. **Vendor Lock-in** - Hard to migrate between clouds
3. **Lambda Pinball** - Excessive function-to-function calls
4. **Grain of Sand** - Overly granular functions
5. **Debugging** - Distributed tracing complexity

### Best Practices
- Keep functions small and single-purpose
- Use proper logging and monitoring (CloudWatch, Datadog)
- Implement proper error handling and retries
- Consider multi-cloud or container-based alternatives
- Use OpenTelemetry for observability

### Security Concerns
- **Insecure code** - Same OWASP risks apply
- **Denial of Wallet** - Cost attacks via excessive invocations
- **Dependency vulnerabilities** - Supply chain attacks
- **Excessive permissions** - Over-privileged IAM roles

---

## 3. Internet of Things (IoT)

### Overview
IoT describes physical objects embedded with sensors, software, and connectivity that enables them to exchange data with other devices over the internet.

### IoT Architecture Layers

1. **Perception Layer** - Sensors and actuators
2. **Network Layer** - Data transmission (WiFi, LoRa, 5G)
3. **Processing Layer** - Edge/fog/cloud computing
4. **Application Layer** - User interfaces and apps

### Key Technologies

**Communication Protocols**
- **MQTT** - Lightweight pub/sub, ideal for low bandwidth
- **CoAP** - Constrained devices, RESTful
- **HTTP/REST** - Standard web protocols
- **LoRaWAN** - Long range, low power
- **Zigbee/Z-Wave** - Home automation mesh
- **5G** - High bandwidth, low latency

**Edge Computing**
- Process data locally on devices
- Reduce latency and bandwidth
- Improve privacy/security

### Major Applications

| Sector | Application | % of Market |
|--------|-------------|-------------|
| Business/Industrial | Asset tracking, fleet management | 22% |
| Utilities | Smart metering | Major |
| Healthcare | Remote monitoring | Growing |
| Smart Home | Thermostats, speakers | Consumer focus |
| Manufacturing | Industrial monitoring | Major |
| Agriculture | Precision farming | Growing |

### Popular IoT Platforms
- **AWS IoT** - AWS IoT Core, Greengrass
- **Azure IoT Hub** - Microsoft ecosystem
- **Google Cloud IoT** - BigQuery integration
- **ThingSpeak** - IoT analytics
- **Home Assistant** - Open source home automation

### Security Concerns

IoT devices are notoriously insecure:
- Default passwords
- No regular updates
- Limited processing for encryption
- Attack surface expansion

**Common Attacks**
- DDoS via botnets (Mirai example)
- Data breaches
- Device hijacking
- Physical harm (medical devices, vehicles)

**Security Best Practices**
- Change default credentials
- Network segmentation
- Regular firmware updates
- Encrypt data in transit
- Use strong authentication

### Future Trends (2026+)
- **Edge AI** - On-device machine learning
- **5G integration** - Massive IoT deployments
- **Digital Twins** - Virtual representations
- **Matter Protocol** - Unified smart home standard
- **Industrial IoT growth** - Industry 4.0 acceleration

---

## Summary

### Graph Databases
Best for: Social networks, fraud detection, recommendations, knowledge graphs
Alternatives: Use relational if data is mostly structured, document stores for flexible schemas

### Serverless
Best for: Event-driven apps, variable workloads, rapid development
Watch out for: Cold starts, vendor lock-in, debugging complexity

### IoT
Best for: Monitoring, automation, real-world data collection
Security is paramount: Never deploy insecure devices to production

---

## References
- Wikipedia: Graph database
- Wikipedia: Serverless computing
- Wikipedia: Internet of things

---

*Report generated: 2026-03-14*
*Researcher Agent*
