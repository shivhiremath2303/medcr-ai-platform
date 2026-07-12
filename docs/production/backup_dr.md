# Backup and Disaster Recovery Strategy

## 1. Backup Strategy

The platform state consists of four main components:

| Component | Type | Backup Method | Frequency |
| :--- | :--- | :--- | :--- |
| **Document Uploads** | Persistent Volume (Files) | CSI Snapshots or `rsync` | Daily |
| **Vector Index (FAISS)** | Persistent Volume (Files) | Snapshots of `/app/data/faiss` | Every 4 hours |
| **Metadata** | Persistent Volume (Files) | Snapshots of `/app/data/metadata` | Daily |
| **Redis** | In-memory + RDB | RDB Snapshots (`/data/dump.rdb`) | Hourly |

### Kubernetes Configuration
- **Helm Values**: Store `my-values.yaml` in a secure Git repository or Vault.
- **Secrets**: Use a tool like `sealed-secrets` or a CSI Secret Store to recreate secrets.

## 2. Disaster Recovery (DR)

### Recovery Point Objective (RPO)
- **Documents**: 24 hours.
- **AI Index**: 4 hours.
- **Session Data (Redis)**: 1 hour.

### Recovery Time Objective (RTO)
- **API Availability**: < 30 minutes (redeploy to new cluster).
- **Full Data Restore**: < 2 hours.

### Recovery Procedures

#### Redis Recovery
1. Restore the `dump.rdb` file to the Redis volume.
2. Restart the Redis pod.

#### FAISS Index Recovery
1. Copy the latest snapshots of `legal_documents.index` and `metadata.json` to the `/app/data/faiss` volume.
2. The backend will automatically load them on startup.

#### Full Cluster Failure
1. Provision a new Kubernetes cluster.
2. Install the NGINX Ingress Controller.
3. Apply Persistent Volume snapshots.
4. Deploy the Helm chart with the existing `values.yaml`.
