"""File operation tools for the agent."""
from pathlib import Path
from typing import Optional
import os
import base64
from pydantic import BaseModel
from pydantic_ai import Agent


class ReadFile(BaseModel):
    """Request to read a file."""
    path: str


class WriteFile(BaseModel):
    """Request to write/create a file."""
    path: str
    content: str


def read_file(request: ReadFile, agent: Agent) -> str:
    """Read file contents with security checks."""
    path = Path(request.path).resolve()
    
    # Security: must be under cwd
    if not path.is_relative_to(Path.cwd().resolve()):
        return "Error: Access denied - path outside working directory."
    
    # Check file exists
    if not path.is_file():
        return f"Error: File not found: {request.path}"
    
    # Security: max 10MB
    file_size = path.stat().st_size
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        return f"Error: File too large ({file_size / 1024 / 1024:.1f}MB > 10MB limit)."
    
    # Try encoding fallback
    try:
        content = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding='latin-1')
        except UnicodeDecodeError:
            # Binary file - return base64
            content = base64.b64encode(path.read_bytes()).decode('utf-8')
            return f"File appears to be binary. Base64 encoded:\n{content[:200]}... (truncated)"
    
    # Truncate output for long files
    if len(content) > 5000 and '\\n' in content:
        lines = content.split("\n")
        if len(lines) > 1997:
            return f"⚠ File is long ({len(lines)} lines)\n\n" + "\n".join(lines[-1997:])
    
    return content


def write_file(request: WriteFile, agent: Agent) -> str:
    """Create or update file with security checks."""
    path = Path(request.path)
    
    # Security: check parent dir is under cwd
    try:
        resolved = path.resolve()
        parent = resolved.parent
        parent.resolve()
    except (OSError, ValueError):
        return f"Error: Cannot resolve path: {request.path}"
    
    if not parent.is_relative_to(Path.cwd().resolve()):
        return "Error: Access denied - destination outside working directory."
    
    # Check file exists and ask for permission
    if path.exists():
        return f"File already exists: {request.path}. Overwrite? (yes/no)"
    
    # Security: max 10MB
    if len(request.content) > 10 * 1024 * 1024:
        return f"Error: Content too large ({len(request.content) / 1024 / 1024:.1f}MB > 10MB limit)."
    
    # Create parent if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write with encoding fallback
    try:
        path.write_text(request.content, encoding='utf-8')
    except UnicodeEncodeError:
        path.write_text(request.content, encoding='latin-1')
    
    return f"File created/updated: {path}\nSize: {len(request.content)} chars"


# Register tools with agent
from typing import get_args, get_origin

# Find the agent instance from cli_ollama_agent
import importlib.util
spec = importlib.util.spec_from_file_location("cli_ollama_agent","/home/hugo/git/pydantic_experiments/src/cli_ollama_agent.py")
module = importlib.util.module_from_spec(spec)

# Register tools on the module
def register_tools(agent):
    agent.tool_plain(ReadFile)(read_file)
    agent.tool_plain(WriteFile)(write_file)
    return agent
