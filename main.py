# DOES NOT RUN YET, NEEDS FIXING!
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.agents import AgentExecutor, create_react_agent  # This REACT agent is better suited for llama models
from tools import search_tool, wiki_tool, save_tool


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    

llm = ChatOllama(
    model="llama3.1",
    temperature=0
)

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.

            You have access to the following tools: {tools}

            Thought: Think about what to do
            Action: One of [{tool_names}]
            Action Input: Input for the tool
            Observation: Result from the tool

            Repeat the Thought/Action/Observation steps as needed.

            Answer the user query and use neccessary tools. 
            When you have gathered enough infomation, produce the final answer.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool]
agent = create_react_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)
query = input(">>> ")
raw_response = agent_executor.invoke({"query": query})
output_text = raw_response.get("output")

try:
    structured_response = parser.parse(output_text)
    print("\nStrictured Response\n")
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)