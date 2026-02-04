from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    instruction="""You're a specialist in Google Search""",
    tools=[google_search],
)

search_agent_tool = AgentTool(search_agent)
