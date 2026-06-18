---
name: gcp-cloud-run-migrator
description: Helps users inspect, plan, and migrate Cloud Run services and their dependencies (secrets, service accounts, enabled APIs, logging policies, container images) from a source GCP project to a target GCP project.
---

# GCP Cloud Run Migrator

An expert skill to safely discover, audit, plan, and replicate Cloud Run services and their dependencies from a source GCP project to a target GCP project.

## Workflow Phases

### Phase 1: Source Service Discovery & Description
Analyze the source Cloud Run service to extract its configuration, env vars, secrets, service accounts, and container image:
1. Run `gcloud run services describe <service_name> --project <source_project> --region <region> --format=json`.
2. Parse the output to identify:
   - **Container Image URL** (e.g., in `spec.template.spec.containers[0].image`).
   - **Runner Service Account** (e.g., in `spec.template.spec.serviceAccountName`).
   - **Environment Variables** (e.g., in `spec.template.spec.containers[0].env`).
   - **Secret References** (e.g., in `spec.template.spec.containers[0].env` pointing to secrets or `spec.template.spec.volumes` mounting secrets).

### Phase 2: Registry & Image Inspection
Examine the container image located in Artifact Registry:
1. Identify the Artifact Registry host, repository, image name, and tag from the image URL.
2. Run `gcloud artifacts docker images list` or `docker pull` to fetch and examine the image locally to inspect metadata, labels, or layers if necessary.
3. Check access controls needed to allow the target project's runner service account to pull from the source Artifact Registry (if cross-project image pulling is required).

### Phase 3: Dependency Auditing & Reference Mapping
Identify all dependent GCP services, API dependencies, and logging policies:
1. **API & Service Dependencies**:
   - Identify dependent backend services, external APIs, databases, or microservices from environment variables or application configuration.
   - For each dependency, ask the user to choose:
     * **Migrate**: Replicate and deploy the dependency in the target project.
     * **Reference**: Continue referencing the existing service/API in the current source project.
2. **Enabled APIs**: List and record the APIs used/enabled in the source project that the app relies on.
3. **Secrets**: For each referenced secret, identify its name and check if it exists in the target project.
4. **Service Accounts**: Audit the runner and deployment service accounts.
5. **Logging & Monitoring**: Check log routing, sinks, or specific logging policies/destinations. Run `gcloud logging sinks list --project <source_project>` to check if logs are being routed to BigQuery, Pub/Sub, or other destinations.

### Phase 4: Migration Planning (Markdown Checklist)
Create a highly-structured, visually appealing markdown migration checklist (e.g., `migration_plan.md`) covering:
- **Service Metadata**: Name, region, source project, target project.
- **Dependency Map**: A list of external APIs or backend services with the user's decision (Migrate vs. Reference) and required URL updates.
- **APIs to Enable** in target project.
- **Service Accounts to Create/Configure** (Runner SA, Deployment SA).
- **Secrets to Replicate** (including value-mapping instructions).
- **Artifact Registry Permissions** (allowing target SA to read source image, or pushing a copy to the target registry).
- **Cloud Run Deployment Command** matching the source configuration.
- **Logging & Monitoring Setup**.

### Phase 5: Target Provisioning & Setup
Automate the replication of dependencies in the target project:
1. **Enable APIs**: Run `gcloud services enable <service> --project <target_project>`.
2. **Create Secrets**: Run `gcloud secrets create <secret_name> --project <target_project>` and ask the user for the values or prompt to fill them securely.
3. **Service Accounts**: Create the target service accounts and grant required roles (e.g., `roles/run.serviceAgent`, `roles/secretmanager.secretAccessor`).
4. **Replicate Log Sinks**: Create corresponding sinks/policies in the target project.

### Phase 6: Interactive Guidance
Always ask the user about:
- Which Service Account should be used as the **Deployment SA** (the pipeline/runner identity).
- Which Service Account should be used as the **Runner SA** (the runtime identity of the container).
- Selection of Migrate vs. Reference for each backend or database dependency.
- Confirmation of Secret Values before creating them in Secret Manager.

### Phase 7: Verification
1. Run `gcloud services list --enabled --project <target_project>` to verify all necessary APIs are active.
2. Run `gcloud secrets list --project <target_project>` to verify all secrets exist.
3. Verify IAM bindings on the target service accounts.
