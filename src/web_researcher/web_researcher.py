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
        sp = '''You are a web web_researcher and an expert writing a market research document. You are
        tasked with creating a comprehensive market research document given a research
        question in the history that contains various information. Your goal is to analyze this question and produce
        a well-structured market research report.

        Important guidelines:
        1. Ignore specific demographic information such as income, age, gender, and vocational details.
        2. Focus on broader market and regional information (country, city, etc.).
        3. Infer the main topic from the research question and conduct your market research based on this.

        Structure your document using the following template:
        
        <template>

        # [Appropriate Title based on the inferred topic]

        ## Introduction

        ## Market Overview
        ### Size of market
        ### Market trends
        ### Consumer demographics
        ### [Optional field for important information]

        ## Competitor Analysis
        ### Key players
        ### Market share
        ### [Optional field for important information]

        ## SWOT Analysis

        ## Regulatory Landscape

        ## Research Key Insights

        ## Summary

        ## Sources
        
        
        #### This report was curated just for you by Laila from Madex.
        
        </template>

        Follow these instructions for creating your document:

        1. Begin with an appropriate title based on the inferred topic.
        2. Use '#' for the document heading, '##' for section titles, and '###' for sub-section titles.
        3. Provide URL sources for every claim made in the report. Write hyperlink sources as shorthand in markdown.
        4. Use Statista, Neilson, Kantar and Euromonitor as primary sources for market data, but don't limit yourself
        to these and use other web sources for relevant information in case primary sources have insufficient details.
        5. In the Market Overview section:
        - Provide specific figures for market size
        - Discuss current and emerging market trends
        - Present consumer demographics with careful sourcing
        - Add an optional field if you find other important market information
        6. In the Competitor Analysis section:
        - List all major and minor competitors
        - Provide market share data where available
        - Include an optional field for other relevant competitive information
        7. In the SWOT Analysis, place emphasis on opportunities in the market.
        8. Discuss the regulatory landscape relevant to the market.
        9. Highlight key insights specific to the market in the given country or region.
        10. Provide a detailed summary of the findings from your research. Be verbose and detailed.  
        If appropriate,
           10 a. Start the summary with a popular marketing quote or a relevant quote from a business leader with a citation.
           10 b. Include recommendations for further research at the end.
        11. List all sources used at the end of the document.

        Remember to provide sources for every claim, and format your document according to
        the structure provided. Your goal is to create a comprehensive, well-sourced, and
        insightful market research document based on the given research question.
        '''
        return self._create_agent(self.llm_researcher, [self.tavily_tool], sp)

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
