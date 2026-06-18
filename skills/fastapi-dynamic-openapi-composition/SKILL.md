---
name: fastapi-dynamic-openapi-composition
description: Expert guidance, production patterns, and test suites for implementing a Dynamic OpenAPI Schema Composition pattern in Python FastAPI projects.
---

# FastAPI Dynamic OpenAPI Spec Aggregator & Schema Composition Guide

## Overview
This skill provides expert procedural guidance, production patterns, and test suites for implementing a **Dynamic OpenAPI Schema Composition** (or Spec Aggregator) pattern in Python FastAPI projects. It enables the agent to programmatically merge native Python route definitions with static YAML-based OpenAPI specifications (located in configuration directories) at runtime, presenting them in a single, unified Swagger/Redoc UI.

## Trigger Conditions
Activate this skill when the user mentions:
- "merge OpenAPI specs", "federate swagger", "dynamic openapi composition"
- "OpenAPI spec merging", "aggregate yaml to FastAPI", "runtime schema composition"
- "unified Swagger UI for dynamic routes"
- "FastAPI dynamic spec aggregator", "FastAPI schema federation"

---

## 🏗️ Architectural Concept

### 1. How to Explain This to a Person (Colleague / Manager)
> "We are using a **Dynamic Spec Aggregation** approach with FastAPI. Instead of manually copying and pasting our static YAML files into our Python code, we configured FastAPI to automatically scan our configuration folder at runtime. It programmatically injects those external YAML paths into its own auto-generated OpenAPI schema. This gives us a single, unified Swagger UI hosted on Cloud Run that documents both our Python code and our configuration-driven endpoints seamlessly."

### 2. How to Explain This to an LLM Agent (Prompt Blueprint)
> "I am building a Python API deployment on Google Cloud Run using FastAPI. I am using a 'Dynamic OpenAPI Schema Aggregation' pattern. The goal is to host a single, unified Swagger UI at the root path (/) that merges two different API declaration sources:
> 1. Native FastAPI route definitions (Python code).
> 2. Multiple static config files located in `./src/config/*.yaml`.
> Please help me implement/refactor this setup. The solution must override `app.openapi` to programmatically merge the `paths` and `components` keys from the YAML files into the base FastAPI OpenAPI dictionary without causing key collisions."

### 3. Key Industry Terms
- **Schema Federation / Aggregation**: Combining multiple disparate API definitions into a single source of truth.
- **Runtime Composition**: Merging the configurations dynamically when the application starts up, rather than hardcoding them beforehand (Build-time compilation).
- **Collision Safeguarding**: Assertive route-check validation that prevents overlapping configurations from silently overwriting critical routes.

---

## 💻 Technical Implementation Reference (FastAPI Code Pattern)

Apply this exact pattern when configuring or refactoring the main application gateway:

```python
import os
import yaml
from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse

def setup_dynamic_openapi(app: FastAPI, config_dir: Path) -> None:
    """Overrides app.openapi to dynamically aggregate external YAML specs."""
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
            
        # 1. Generate base OpenAPI schema from native FastAPI routes
        base_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # 2. Scan and merge static YAML configs
        if config_dir.exists():
            for yaml_file in config_dir.glob("*.yaml"):
                with open(yaml_file, "r") as f:
                    try:
                        external_spec = yaml.safe_load(f)
                        if not external_spec:
                            continue
                            
                        # Merge Paths with Collision Detection
                        if "paths" in external_spec:
                            for path, methods in external_spec["paths"].items():
                                if path in base_schema["paths"]:
                                    raise ValueError(f"Path collision detected: {path}")
                                base_schema["paths"][path] = methods
                                
                        # Merge Components (Deep Merging schemas to avoid shallow overwrite)
                        if "components" in external_spec:
                            if "components" not in base_schema:
                                base_schema["components"] = {}
                            
                            for comp_type, comp_vals in external_spec["components"].items():
                                # e.g. comp_type = 'schemas', 'securitySchemes', 'parameters'
                                if comp_type not in base_schema["components"]:
                                    base_schema["components"][comp_type] = {}
                                
                                # Perform recursive-like updating for component dictionary
                                base_schema["components"][comp_type].update(comp_vals)
                                
                    except yaml.YAMLError as exc:
                        print(f"Error parsing OpenAPI spec {yaml_file.name}: {exc}")
                        raise exc
                        
        app.openapi_schema = base_schema
        return app.openapi_schema

    app.openapi = custom_openapi
```

---

## 🧪 Comprehensive Pytest Suite

Use this complete test suite to validate the implementation.

```python
import os
import yaml
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pathlib import Path

# --- Setup Fixtures ---

@pytest.fixture
def mock_yaml_configs(tmp_path):
    """Creates temporary YAML configs for testing in a temporary directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    mock_yaml_content = """
    paths:
      /api/yaml-injected:
        get:
          summary: "Injected from YAML"
          responses:
            '200':
              description: "Success"
    components:
      schemas:
        InjectedModel:
          type: object
          properties:
            id:
              type: string
    """
    
    test_file = config_dir / "test_api.yaml"
    test_file.write_text(mock_yaml_content)
    
    return config_dir


# --- Unit Tests ---

def test_yaml_files_are_valid_syntax(mock_yaml_configs):
    """Ensures all configuration files in the config folder are structurally valid YAML."""
    for yaml_file in mock_yaml_configs.glob("*.yaml"):
        with open(yaml_file, "r") as f:
            try:
                data = yaml.safe_load(f)
                assert isinstance(data, dict), f"YAML file {yaml_file.name} must parse to a dictionary"
            except yaml.YAMLError as exc:
                pytest.fail(f"Invalid YAML syntax in {yaml_file.name}: {exc}")


def test_dynamic_openapi_schema_merges_successfully(mock_yaml_configs):
    """Tests if the custom app.openapi() method correctly injects YAML paths and components."""
    app = FastAPI(title="Unified API")

    @app.get("/api/native")
    def native_route():
        return {"message": "Native FastAPI route"}

    from .main import setup_dynamic_openapi  # Adjust import based on project layout
    setup_dynamic_openapi(app, mock_yaml_configs)
    
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    
    # 1. Verify native route exists
    assert "/api/native" in schema["paths"]
    
    # 2. Verify dynamically injected YAML route exists
    assert "/api/yaml-injected" in schema["paths"]
    assert schema["paths"]["/api/yaml-injected"]["get"]["summary"] == "Injected from YAML"
    
    # 3. Verify component schema merged successfully
    assert "InjectedModel" in schema["components"]["schemas"]


def test_openapi_schema_collision_detection(mock_yaml_configs):
    """Tests that a ValueError is raised if a YAML file attempts to overwrite a native route."""
    app = FastAPI(title="Unified API")

    @app.get("/api/native")
    def native_route():
        return {"message": "Native FastAPI route"}

    # Create a malicious YAML file that tries to overwrite the native route
    collision_yaml = """
    paths:
      /api/native:
        get:
          summary: "I am trying to overwrite your route!"
    """
    collision_file = mock_yaml_configs / "collision.yaml"
    collision_file.write_text(collision_yaml)
    
    from .main import setup_dynamic_openapi  # Adjust import based on project layout
    setup_dynamic_openapi(app, mock_yaml_configs)
    
    with pytest.raises(ValueError, match=r"Path collision detected: /api/native"):
        # Trigger the openapi generation which should catch the collision
        app.openapi()
```

---

## 🔧 Debugging Analysis & Key Considerations

1. **Path Collisions (Fail-Fast Policy)**:
   - If a YAML file maps to an existing Python endpoint, it raises a `ValueError`. This prevents silent overwriting of core routes.
   
2. **Shallow vs. Deep Component Merging**:
   - Standard dictionary updates (`dict.update()`) do a shallow update.
   - **Mitigation Pattern**: Ensure you iterate and merge one level deeper into sub-keys (e.g. `components["schemas"]`, `components["securitySchemes"]`, `components["parameters"]`) separately as implemented in the technical reference block.
