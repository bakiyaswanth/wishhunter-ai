"""Sandbox Code Execution service for WishHunter AI.

Configures AgentEngineSandboxCodeExecutor and direct sandbox execution
pointing to the Agent Engine sandbox provisioned from deployment_metadata.json.
"""

import json
import vertexai
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

PROJECT_ID = "qwiklabs-gcp-04-28d6773dbc5b"
LOCATION = "us-east1"
AGENT_ENGINE_ID = "projects/487984042953/locations/us-east1/reasoningEngines/350767299004727296"
SANDBOX_RESOURCE_NAME = (
    "projects/487984042953/locations/us-east1/reasoningEngines/350767299004727296/sandboxEnvironments/3295130795328405504"
)


def get_sandbox_code_executor() -> AgentEngineSandboxCodeExecutor:
    """Return an AgentEngineSandboxCodeExecutor configured for the Agent Engine sandbox."""
    return AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME
    )


def run_python_in_sandbox(python_code: str) -> dict:
    """Execute Python code safely in the isolated Agent Engine Sandbox environment.

    Args:
        python_code: Executable Python code string. Use print() to output results.

    Returns:
        Dict with stdout, stderr, and status.
    """
    try:
        client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
        resp = client.agent_engines.sandboxes.execute_code(
            name=SANDBOX_RESOURCE_NAME,
            input_data={"code": python_code},
        )
        stdout = ""
        stderr = ""
        for output in resp.outputs:
            if output.mime_type == "application/json":
                data = json.loads(output.data.decode("utf-8"))
                stdout += data.get("msg_out", "")
                stderr += data.get("msg_err", "")
        return {
            "status": "success",
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stdout": "",
            "stderr": "",
        }
