# MCP Connector: Integrating AI agent with Data Warehouse in Microsoft Fabric

This repo demonstrates the integration of an Azure OpenAI-powered AI agent with a Microsoft Fabric data warehouse using the Model Context Protocol (MCP).

MCP enables dynamic discovery of tools, data resources and prompt templates (with more coming), unifying their integration with AI agents. GraphQL provides an abstraction layer for universal data connection. Below, you will find detailed steps on how to combine MCP and GraphQL to enable bidirectional access to enterprise data for your AI agent.

> [!NOTE]
> In the MCP server's script, some query parameter values are hard-coded for the sake of this example. In a real-world scenario, these values would be dynamically generated or retrieved.

## Table of contents:
- [Part 1: Configuring Microsoft Fabric Backend]()
- [Part 2: Configuring Local Client Environment]()
- [Part 3: User Experience - Gradio UI]()
- [Part 4: Demo video on YouTube]()

## Part 1: Configuring Microsoft Fabric Backend
1. In Microsoft Fabric create a new data warehouse pre-populated by sample data by clicking *New item -> Sample warehouse*:
![Step1_SampleWarehouse](images/Step1_SampleWarehouse.png)
2. Next, create a GraphQL API endpoint by clicking *New item -> API for GraphQL*:
![Step2_GraphQlCreate](images/Step2_GraphQLCreate.png)
3. In the data configuration of GraphQL API, choose *Trip (dbo.Trip)* table:
![Step3_GraphQLData.png](images/Step3_GraphQLData.png)
4. Copy endpoint URL of your GraphQL API:
![Step4_GraphQLDataURL.png](images/Step4_GraphQLDataURL.png)

## Part 2: Configuring Local Client Environment
1. Install the required Python packages, listed in the provided *requirements.txt*:
```PowerShell
pip install -r requirements.txt
```
2. Configure environmnet variables for MCP client:

| Variable                | Description                                      |
| ----------------------- | ------------------------------------------------ |
| `AOAI_API_BASE`         | Base URL of the Azure OpenAI endpoint            |
| `AOAI_API_VERSION`      | API version of the Azure OpenAI endpoint         |
| `AOAI_DEPLOYMENT`       | Deployment name of the Azure OpenAI model        |

3. Update the value of `AZURE_FABRIC_GRAPHQL_ENDPOINT` variable in the provided *.env* file with GraphQL's endpoint URL from Step 1.4 above. It will be utilised by MCP Server script to establish connectivity with Microsoft Fabric.

## Part 3: User Experience - Gradio UI
1. Launch MCP client in your command prompt:
``` PowerShell
python MCP_Client_Gradio.py
```
2. Click *Initialise System* button to start MCP server and connect your AI agent to Microsoft Fabric's GraphQL API endpoint:
![Step5_GradioLaunch.png](images/Step5_GradioLaunch.png)
3. You can now pull and push data to your data warehouse using GraphQL's queries and mutations enabled by this demo MCP connector:

## Part 4: Demo video on YouTube

