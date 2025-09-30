from mcp.server.fastmcp import FastMCP
import subprocess
import os
import argparse
from typing import List

mcp = FastMCP("version_control")
ALLOWED_PATHS: List[str] = []


def is_git_repo(path: str) -> bool:
    """Verifica si la ruta es un repositorio git."""
    return os.path.isdir(os.path.join(path, ".git"))


def is_allowed_path(path: str) -> bool:
    """Verifica si la ruta está permitida."""
    abs_path = os.path.abspath(path)
    return any(
        abs_path.startswith(os.path.abspath(allowed)) for allowed in ALLOWED_PATHS
    )


def run_git_command(args, cwd=None):
    """Ejecuta un comando git y retorna la salida."""
    if cwd:
        if not is_allowed_path(cwd):
            return f"Error: {cwd} no está permitido."
        if not is_git_repo(cwd):
            return f"Error: {cwd} no es un repositorio git."
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout.strip()


@mcp.tool()
async def git_status(path: str = ".") -> str:
    """Muestra el estado actual del repositorio git en la ruta dada."""
    return run_git_command(["status"], cwd=path)


@mcp.tool()
async def git_log(n: int = 5, path: str = ".") -> str:
    """Muestra los últimos n commits del repositorio en la ruta dada."""
    return run_git_command(["log", f"-{n}", "--oneline"], cwd=path)


@mcp.tool()
async def git_diff(path: str = ".") -> str:
    """Muestra las diferencias no confirmadas en el repositorio en la ruta dada."""
    return run_git_command(["diff"], cwd=path)


@mcp.tool()
async def git_branch(path: str = ".") -> str:
    """Lista las ramas locales del repositorio en la ruta dada."""
    return run_git_command(["branch"], cwd=path)


@mcp.tool()
async def git_checkout(branch: str, path: str = ".") -> str:
    """Cambia a la rama especificada en la ruta dada."""
    return run_git_command(["checkout", branch], cwd=path)


@mcp.resource("version-control://allowed-paths")
def allowed_paths() -> List[str]:
    """Devuelve la lista de rutas permitidas para operaciones git."""
    return ALLOWED_PATHS


@mcp.prompt()
async def version_control_prompt() -> str:
    """Prompt para gestión de control de versiones."""
    return (
        "Eres un asistente para control de versiones con git. Puedes:\n"
        "1. Ver el estado del repositorio\n"
        "2. Ver el historial de commits\n"
        "3. Ver diferencias\n"
        "4. Listar ramas\n"
        "5. Cambiar de rama\n"
        "Puedes indicar la ruta del repositorio con el parámetro 'path'.\n"
        "¿Qué operación de git necesitas realizar?"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de control de versiones MCP")
    parser.add_argument(
        "--allowed-paths",
        nargs="+",
        required=True,
        help="Lista de rutas permitidas para operaciones git",
    )
    args = parser.parse_args()
    ALLOWED_PATHS = args.allowed_paths
    mcp.run(transport="stdio")
