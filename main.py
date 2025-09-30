import asyncio
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
from agent_state import get_agent_state
import streamlit as st


async def main():
    await app.initialize()

    state = await get_agent_state(
        key="agent",
        agent_class=Agent,
        llm_class=GoogleAugmentedLLM,
        name="agent",
        instruction="""Eres un asistente especializado en la gestión de tareas. 
        Puedes añadir nuevas tareas, listar todas las tareas pendientes, marcar tareas como completadas y eliminar tareas de la lista. 
        Responde siempre de forma clara y concisa, guiando al usuario sobre las acciones que puede realizar. 
        Utiliza las herramientas disponibles para manipular la lista de tareas y proporciona resúmenes cuando sea necesario. 
        Si el usuario no especifica una acción, sugiere opciones como: añadir, listar, completar o eliminar tareas.
        """,
        server_names=["version_control"],
    )

    tools = await state.agent.list_tools()
    resources = await state.agent.list_resources()

    st.title("💬 Agent chatbot")

    with st.expander("View Tools"):
        st.markdown(
            "".join(
                [f"- **{tool.name}**: {tool.description}\n" for tool in tools.tools]
            )
        )

    st.sidebar.title("Recursos disponibles")
    resource_names = [resource.name for resource in resources.resources]
    selected_resource = st.sidebar.selectbox("Selecciona un recurso", resource_names)
    include_resource = st.sidebar.checkbox("Incluir recurso en el chat")

    if selected_resource:
        resource = next(r for r in resources.resources if r.name == selected_resource)
        st.sidebar.markdown(f"**Descripción:** {resource.description}")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Type your message here..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})

        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            response = ""
            with st.spinner("Thinking..."):

                full_prompt = prompt
                if include_resource and selected_resource:
                    resource_content = await state.agent.read_resource(
                        uri=str(resource.uri)
                    )
                    full_prompt = (
                        f"[Recurso seleccionado: {resource.name}]\n"
                        f"{resource_content}\n\n"
                        f"{prompt}"
                    )
                response = await state.llm.generate_str(
                    message=full_prompt, request_params=RequestParams(use_history=True)
                )
            st.markdown(response)

        st.session_state["messages"].append({"role": "assistant", "content": response})


if __name__ == "__main__":
    app = MCPApp(name="mcp_streamlit_agent")
    asyncio.run(main())
