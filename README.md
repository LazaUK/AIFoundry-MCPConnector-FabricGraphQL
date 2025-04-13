# MCP Connector: Integrating AI agent with Data Warehouse in Microsoft Fabric

This repo demonstrates the integration of an Azure OpenAI-powered AI agent with a Microsoft Fabric data warehouse using the Model Context Protocol (MCP).

MCP enables dynamic discovery of tools, data resources and prompt templates (with more coming), unifying their integration with AI agents. GraphQL provides an abstraction layer for universal data connection. Below, you will find detailed steps on how to combine MCP and GraphQL to enable bidirectional access to enterprise data for your AI agent.

> [!NOTE]
> The 

## Table of contents:
- [Part 1: Configuring Microsoft Fabric Backend]()
- [Part 2: Configuring Local Client Environment]()
- [Part 3: User Experience - Gradio UI]()
- [Part 4: Demo video on YouTube]()

## Part 1: Configuring Microsoft Fabric Backend


## Part 2: Configuring Local Client Environment
1. Install the required Python packages, listed in provided *requirements.txt*:
```powershell
pip install requirements.txt
```
2. Configure environmnet variables for MCP client:

| Variable                | Description                                      |
| ----------------------- | ------------------------------------------------ |
| `AOAI_API_BASE`         | Azure subscription ID.                           |
| `AOAI_API_VERSION`      | Azure ML resource group name.                    |
| `AOAI_DEPLOYMENT`       | Azure ML workspace name.                         |

3. Update the value of AZURE_FABRIC_GRAPHQL_ENDPOINT variable in .env file with GraphQL endpoint's .

## Part 3: User Experience - Gradio UI

## Part 4: Demo video on YouTube

