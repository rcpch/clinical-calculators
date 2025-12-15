from __future__ import annotations

import json
from typing import Any

import markdown as md

# Third-party imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

# local imports
from core.generator import generate_calculator
from core.loader import (
    DependencyError,
    available_calculators,
    get_calculator_spec,
    load_calculator_module,
    parse_inputs_spec,
)


class ReverseProxyRootPathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        forwarded_prefix = request.headers.get("X-Forwarded-Prefix", "")
        if forwarded_prefix:
            request.scope["root_path"] = forwarded_prefix
        response = await call_next(request)
        return response


# Initialize rate limiter
# Permissive limits as calculators are heavily used, but guards against attacks
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Clinical Calculators API",
    summary="Clinical calculators, standardised and reusable.",
    version="0.0.1",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    servers=[{"url": "/clinical-calculators"}],
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ReverseProxyRootPathMiddleware)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon(request: Request):
    root_path = request.scope.get("root_path", "")
    return HTMLResponse(url=f"{root_path}/static/favicon.ico")


# Prefix-aware Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request) -> HTMLResponse:
    root_path = request.scope.get("root_path", "")
    return get_swagger_ui_html(
        openapi_url=f"{root_path}{app.openapi_url}",
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=f"{root_path}/docs/oauth2-redirect",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()


# Prefix-aware ReDoc
@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html(request: Request) -> HTMLResponse:
    root_path = request.scope.get("root_path", "")
    return get_redoc_html(
        openapi_url=f"{root_path}{app.openapi_url}",
        title=f"{app.title} - ReDoc",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):  # UPDATED
    root_path = request.scope.get("root_path", "")
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Clinical Calculators</title>
                <link rel="icon" href="{root_path}/static/favicon.ico" />
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }}
                    a {{ color: #0969da; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    ul {{ line-height: 1.8; }}
                </style>
            </head>
            <body>
                <h1>Clinical Calculators</h1>
                <p>Welcome! Choose where to go:</p>
                <ul>
                    <li><a href="{root_path}/docs">Swagger UI</a> (interactive API docs)</li>
                    <li><a href="{root_path}/redoc">ReDoc</a> (alternative API docs)</li>
                    <li><a href="{root_path}/openapi.json">OpenAPI JSON</a></li>
                    <li><a href="{root_path}/list.html">List Calculators (HTML)</a></li>
                    <li><a href="{root_path}/list">List calculators (JSON)</a></li>
                </ul>
            </body>
        </html>
        """
    )


@app.get("/list")
def list_calculators():
    return available_calculators()


@app.get("/{name}/doc")
def calculator_doc(name: str):
    spec = get_calculator_spec(name)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Calculator '{name}' not found")
    return {"name": name, "doc": spec.doc_config}


@app.post("/calculate")
@limiter.limit("100/minute")  # Permissive limit for heavy calculator usage
def calculate(request: Request, payload: dict[str, Any]):
    name = payload.get("calculator")
    params = payload.get("params", {})
    if not name:
        raise HTTPException(status_code=400, detail="Missing 'calculator' in payload")

    try:
        mod = load_calculator_module(name)
    except ModuleNotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Calculator '{name}' not found"
        ) from e
    except DependencyError as de:
        # 424 Failed Dependency conveys installation issue
        raise HTTPException(status_code=424, detail=str(de)) from de

    if not hasattr(mod, "calculate"):
        raise HTTPException(
            status_code=500, detail=f"Calculator '{name}' missing calculate()"
        )

    try:
        resp = mod.calculate(params)  # type: ignore[attr-defined]
        return resp.dict() if hasattr(resp, "dict") else resp
    except Exception as e:  # validation errors surfaced as 400
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/generate-calculator")
@limiter.limit("10/minute")  # Lower limit for resource-intensive generation
def generate_calculator_endpoint(request: Request, payload: dict[str, Any]):
    """
    Generate calculator code from TOML/Markdown specification.

    Request body:
    {
        "spec": "TOML/Markdown specification string"
    }

    Returns:
    {
        "success": true/false,
        "name": "calculator_name",
        "python_code": "generated calculator code",
        "test_code": "generated test code",
        "validation_errors": [...],
        "message": "Success or error message"
    }
    """
    spec_input = payload.get("spec")

    if not spec_input:
        raise HTTPException(status_code=400, detail="Missing 'spec' in request body")

    # Generate calculator
    result = generate_calculator(spec_input)

    # Format validation errors for response
    errors = [
        {
            "field": e.field,
            "message": e.message,
            "severity": e.severity,
        }
        for e in result.validation_errors
    ]

    # Determine response message
    if not result.is_valid:
        message = "Calculator generation failed. Please fix the errors and try again."
        status_code = 400
    elif errors:
        message = "Calculator generated successfully with warnings."
        status_code = 200
    else:
        message = "Calculator generated successfully!"
        status_code = 200

    response = {
        "success": result.is_valid,
        "name": result.name,
        "python_code": result.python_code,
        "test_code": result.test_code,
        "validation_errors": errors,
        "message": message,
    }

    if not result.is_valid:
        raise HTTPException(status_code=status_code, detail=response)

    return response


@app.get("/{name}/doc.html", response_class=HTMLResponse)
def calculator_doc_html(name: str, request: Request):  # UPDATED
    spec = get_calculator_spec(name)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Calculator '{name}' not found")
    body_md = spec.doc_config or f"# {name}\n\nNo documentation available."
    body_html = md.markdown(body_md, extensions=["fenced_code", "tables", "toc"])
    root_path = request.scope.get("root_path", "")
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>{name} – Clinical Calculator Docs</title>
            <link rel="icon" href="{root_path}/static/favicon.ico" />
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }}
                pre {{ background: #0d1117; color: #c9d1d9; padding: 1rem; overflow: auto; border-radius: 6px; }}
                code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
                h1, h2, h3 {{ line-height: 1.2; }}
                .container {{ display: block; }}
            </style>
        </head>
        <body>
            <div class="container">{body_html}</div>
        </body>
    </html>
    """
    return HTMLResponse(html)


@app.get("/list.html", response_class=HTMLResponse)
def calculators_docs_index(request: Request):  # UPDATED
    calcs = available_calculators()
    root_path = request.scope.get("root_path", "")
    items = "\n".join(
        f"<li><strong>{name}</strong> — {title} [<a href='{root_path}/{name}/doc.html'>docs</a>] [<a href='{root_path}/{name}/form'>form</a>]</li>"
        for name, title in sorted(calcs.items(), key=lambda x: x[0])
    )
    html = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Clinical Calculators – Docs Index</title>
                <link rel="icon" href="{root_path}/static/favicon.ico" />
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }}
                    h1 {{ margin-bottom: 1rem; }}
                    ul {{ line-height: 1.8; }}
                    a {{ text-decoration: none; color: #0969da; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h1>Clinical Calculators – Documentation</h1>
                <p>Click a calculator to view its documentation:</p>
                <ul>
                    {items}
                </ul>
            </body>
        </html>
        """
    return HTMLResponse(html)


@app.get("/{name}/form", response_class=HTMLResponse)
def calculator_form(name: str, request: Request):  # UPDATED
    spec = get_calculator_spec(name)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Calculator '{name}' not found")
    fields = parse_inputs_spec(spec.doc_config)

    def input_control(f: dict[str, Any]) -> str:
        label = f.get("description") or f.get("name")
        fname = f.get("name")
        ftype = (f.get("type") or "string").lower()
        required = "required" if f.get("required") else ""
        placeholder = f.get("unit") or ""
        if isinstance(f.get("enum"), list) and f["enum"]:
            opts = "".join(f"<option value='{opt}'>{opt}</option>" for opt in f["enum"])
            return f"<label>{label}: <select name='{fname}' {required}>{opts}</select></label>"
        input_type = "number" if ftype in {"number", "float", "int"} else "text"
        min_attr = (
            f" min='{f['min']}'" if isinstance(f.get("min"), (int, float)) else ""
        )
        max_attr = (
            f" max='{f['max']}'" if isinstance(f.get("max"), (int, float)) else ""
        )
        step_attr = " step='any'" if input_type == "number" else ""
        return f"<label>{label}: <input name='{fname}' type='{input_type}' placeholder='{placeholder}' {required}{min_attr}{max_attr}{step_attr}></label>"

    controls = "<br>\n".join(input_control(f) for f in fields)
    root_path = request.scope.get("root_path", "")
    html = f"""
    <!DOCTYPE html>
    <html lang="en"><head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>{name} – Form</title>
      <link rel="icon" href="{root_path}/static/favicon.ico" />
    </head><body>
      <h1>{name} – Calculator</h1>
      <form method="post" action="{root_path}/{name}/submit">
        {controls}
        <br><br>
        <button type="submit">Calculate</button>
      </form>
      <p>Docs: <a href="{root_path}/{name}/doc.html">View documentation</a></p>
    </body></html>
    """
    return HTMLResponse(html)


@app.post("/{name}/submit", response_class=HTMLResponse)
async def calculator_submit(name: str, request: Request):
    # Accept form or JSON payload and coerce simple numeric types
    try:
        ctype = request.headers.get("content-type", "")
        if "application/json" in ctype:
            params: dict[str, Any] = await request.json()
        else:
            form = await request.form()
            params = {k: v for k, v in form.items()}

        spec = get_calculator_spec(name)
        if not spec:
            return HTMLResponse(
                f"<pre>Calculator '{name}' not found</pre>", status_code=404
            )

        fields = parse_inputs_spec(spec.doc_config or "")
        numeric_names: set[str] = set()
        for f in fields:
            ftype = str(f.get("type", "")).lower()
            fname = f.get("name")
            if fname and ftype in {"number", "float", "int"}:
                numeric_names.add(fname)

        for k, v in list(params.items()):
            if k in numeric_names:
                try:
                    params[k] = float(v)  # best-effort float coercion
                except Exception:
                    pass
    except Exception as e:
        return HTMLResponse(
            f"<pre>Unexpected error while reading input: {str(e)}</pre>",
            status_code=500,
        )

    try:
        mod = load_calculator_module(name)
    except ModuleNotFoundError:
        return HTMLResponse(
            f"<pre>Calculator '{name}' not found</pre>", status_code=404
        )
    except DependencyError as de:
        return HTMLResponse(f"<pre>{str(de)}</pre>", status_code=424)

    try:
        resp = mod.calculate(params)  # type: ignore[attr-defined]
        data = resp.dict() if hasattr(resp, "dict") else resp
        body = json.dumps(data, indent=2, ensure_ascii=False)
        return HTMLResponse(f"<pre>{body}</pre>")
    except Exception as e:
        return HTMLResponse(f"<pre>Error: {str(e)}</pre>", status_code=400)


@app.post("/generate-enhanced-tests")
@limiter.limit("5/minute")
async def generate_enhanced_tests(
    request: Request,
    body: dict[str, Any],
):
    """
    Generate enhanced tests using Ollama LLM.

    Takes calculator spec and generated code, returns LLM-enhanced test code.
    """
    from core.ollama_service import ollama_service

    try:
        spec = body.get("spec")
        calculator_code = body.get("calculator_code")

        if not spec or not calculator_code:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: spec and calculator_code",
            )

        # Generate enhanced tests using Ollama
        enhanced_tests = await ollama_service.generate_tests(spec, calculator_code)

        return {
            "success": True,
            "test_code": enhanced_tests,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate enhanced tests: {str(e)}",
        ) from e


@app.post("/submit-calculator")
@limiter.limit("3/minute")
async def submit_calculator(
    request: Request,
    body: dict[str, Any],
):
    """
    Submit calculator by triggering GitHub Actions workflow to create PR.

    Takes calculator name, code, tests, spec, and optional submitter info.
    Returns workflow dispatch status.
    """
    from core.pr_service import PRSubmissionError, get_pr_service

    try:
        name = body.get("name")
        calculator_code = body.get("calculator_code")
        test_code = body.get("test_code")
        spec = body.get("spec")
        description = body.get("description")

        if not all([name, calculator_code, test_code, spec, description]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: name, calculator_code, test_code, spec, description",
            )

        # Get optional submitter information
        submitter_github = body.get("submitter_github")
        submitter_name = body.get("submitter_name")
        submitter_affiliation = body.get("submitter_affiliation")

        # Submit calculator and trigger workflow
        pr_service = get_pr_service()
        result = await pr_service.submit_calculator(
            name=name,
            calculator_code=calculator_code,
            test_code=test_code,
            spec=spec,
            description=description,
            submitter_github=submitter_github,
            submitter_name=submitter_name,
            submitter_affiliation=submitter_affiliation,
        )

        return {
            "success": True,
            **result,
        }

    except PRSubmissionError as e:
        error_msg = str(e)
        print(f"PR Submission Error: {error_msg}")  # Log for debugging
        raise HTTPException(
            status_code=500,
            detail=error_msg,
        ) from e
    except Exception as e:
        error_msg = f"Failed to submit calculator: {str(e)}"
        print(f"Unexpected Error: {error_msg}")  # Log for debugging
        raise HTTPException(
            status_code=500,
            detail=error_msg,
        ) from e
