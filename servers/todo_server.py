from mcp.server.fastmcp import FastMCP

mcp = FastMCP("todo")

# Lista simple en memoria
todo_list = []
next_id = 1


@mcp.tool()
async def add_task(description: str) -> str:
    """Añade una nueva tarea a la lista"""
    global next_id
    task = {"id": next_id, "description": description, "completed": False}
    todo_list.append(task)
    next_id += 1
    return f"Tarea añadida: {description} (ID: {task['id']})"


@mcp.tool()
async def list_tasks() -> str:
    """Muestra todas las tareas"""
    if not todo_list:
        return "No hay tareas en la lista"

    result = "Lista de tareas:\n"
    for task in todo_list:
        status = "✓" if task["completed"] else "○"
        result += f"{status} [{task['id']}] {task['description']}\n"
    return result


@mcp.tool()
async def complete_task(task_id: int) -> str:
    """Marca una tarea como completada"""
    for task in todo_list:
        if task["id"] == task_id:
            task["completed"] = True
            return f"Tarea {task_id} marcada como completada"
    return f"Tarea con ID {task_id} no encontrada"


@mcp.tool()
async def delete_task(task_id: int) -> str:
    """Elimina una tarea de la lista"""
    global todo_list
    for i, task in enumerate(todo_list):
        if task["id"] == task_id:
            deleted_task = todo_list.pop(i)
            return f"Tarea eliminada: {deleted_task['description']}"
    return f"Tarea con ID {task_id} no encontrada"


@mcp.prompt()
async def task_manager() -> str:
    """Prompt para gestionar tareas"""
    return """Eres un asistente de gestión de tareas. Puedes:
1. Añadir nuevas tareas
2. Listar todas las tareas
3. Marcar tareas como completadas
4. Eliminar tareas

¿Qué te gustaría hacer con tu lista de tareas?"""


@mcp.resource("todo://current")
async def get_current_todos() -> str:
    """Recurso que muestra las tareas actuales en formato JSON"""
    import json

    return json.dumps(todo_list, indent=2, ensure_ascii=False)


@mcp.resource("todo://summary")
async def get_todo_summary() -> str:
    """Recurso con resumen de tareas"""
    total = len(todo_list)
    completed = sum(1 for task in todo_list if task["completed"])
    pending = total - completed

    return f"""=== RESUMEN DE TAREAS ===
Total de tareas: {total}
Completadas: {completed}
Pendientes: {pending}
Porcentaje completado: {(completed/total*100) if total > 0 else 0:.1f}%"""


if __name__ == "__main__":
    mcp.run(transport="stdio")
