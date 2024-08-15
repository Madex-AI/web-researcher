from typing import Annotated, Sequence, TypedDict
import functools
import operator

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI
from langgraph.constants import END, START
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

class WebResearcher:
    def __init__(self):
        self.tavily_tool = TavilySearchResults(max_results=20)
        self.python_repl_tool = PythonREPLTool()

        self.llm_supervisor = ChatOpenAI(model="gpt-4o-mini")
        self.llm_researcher = ChatOpenAI(model="gpt-4o")

        self.members = ["Researcher"]

        self.supervisor_chain = self._create_supervisor_chain()
        self.research_agent = self._create_research_agent()
        self.workflow = self._create_workflow()

    def _create_supervisor_chain(self):
        system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers:  {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
        )
        options = ["FINISH"] + self.members
        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": options},
                        ],
                    }
                },
                "required": ["next"],
            },
        }
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options), members=", ".join(self.members))

        return (
            prompt
            | self.llm_supervisor.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
        )

    def _create_research_agent(self):
        sp = '''You are a web web_researcher and an expert writing a market research document. 
        You will be given a research objective with a lot of information. Some of that information might need dot be ignored. 
    
        IGNORE: income, age, gender, vecational etc. demographic information.
        CONSIDER: Broader market and region (country, city etc.)

        This is your topic, and your objective is to perform market research on the inferred topic topic. 
        Always provide sources alongside claims. Every claim must have a source. Write hyperlink sources as shorthand in markdown. Also include sources at bottom of page.
        Statista and Euromonitor are good sources for market data, though don't limit yourself to them.
        Always start with an appropriate title.
        Given the research objective, search the web to provide details for the following fields noted with -, with subfields (where needed) noted with *. 

        -Introduction

        -Market Overview
        *Size of market
        *Market trends
        *Consumer demographics (age, gender, income, etc. - sourcing is critical here) 
        *(Optional field for things you deem important)

        -Competitor Analysis
        *Key players (list all major and minor competitors)
        *Market share
        *(Optional field for things you deem important)

        -SWOT Analysis (emphasis on opportunities)

        -Regulatory Landscape

        -Key Insights/Quirks of the market in this country or region 

        -Summary
        '''
        return self._create_agent(self.llm_researcher, [self.tavily_tool], sp)
    
    """    
    def _create_research_agent(self):
        sp = '''You are a web web_researcher and an expert writing a market research document. 
        You will be given a topic and your objective is to perform market research on the provided topic. 
        Always provide sources alongside claims. Every claim must have a source. Write hyperlink sources as shorthand in markdown. Also include sources at bottom of page.
        Statista and Euromonitor are good sources for market data, though don't limit yourself to them.
        Always start with an appropriate title.
        Given the research objective, search the web to provide details for the following fields noted with -, with subfields (where needed) noted with *. 

        -Introduction

        -Market Overview
        *Size of market
        *Market trends
        *Consumer demographics (age, gender, income, etc. - sourcing is critical here) 
        *(Optional field for things you deem important)

        -Competitor Analysis
        *Key players (list all major and minor competitors)
        *Market share
        *(Optional field for things you deem important)

        -SWOT Analysis (emphasis on opportunities)

        -Regulatory Landscape

        -Key Insights/Quirks of the market in this country or region 

        -Summary
        '''
        return self._create_agent(self.llm_researcher, [self.tavily_tool], sp)
    """
    def _create_agent(self, llm: ChatOpenAI, tools: list, system_prompt: str):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = create_openai_tools_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools)
        return executor

    def _create_workflow(self):
        workflow = StateGraph(AgentState)
        research_node = functools.partial(self.agent_node, agent=self.research_agent, name="Researcher")
        workflow.add_node("Researcher", research_node)
        workflow.add_node("supervisor", self.supervisor_chain)

        for member in self.members:
            workflow.add_edge(member, "supervisor")

        conditional_map = {k: k for k in self.members}
        conditional_map["FINISH"] = END
        workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
        workflow.add_edge(START, "supervisor")

        return workflow.compile()

    def agent_node(self, state, agent, name):
        result = agent.invoke(state)
        return {"messages": [HumanMessage(content=result["output"], name=name)]}

    def perform_research(self, research_question: str):
        initial_state = {"messages": [HumanMessage(content=research_question)]}
        r0 = self.workflow.invoke(initial_state)
        research_md = r0['messages'][1].content
        return research_md
