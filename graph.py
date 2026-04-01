from typing import TypedDict,Annotated
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END,add_messages
import os
from tools import runner_tool,File_Output
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_openai import ChatOpenAI
import sys
import subprocess
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gemini-2.5-flash",
    base_url=os.getenv("GEMINI_BASE_URL"),
    api_key=os.getenv("GEMINI_API_KEY"),
)


class Graph:
    
    class State(TypedDict):
        messages : Annotated[list,add_messages]
        csv_file : str
        output : str


    def __init__(self):
        self.graph = self._build_graph()
    @staticmethod
    @tool
    def execute_code(csv_file : str):
        """
        Execute a shell command and return the output.
        Use this for system commands, file operations, etc.
        
        Args:
            csv_file_path : The csv file you should analyse    
        Returns:
            The output of the command or error message
        """
        script = "extract_column.py"
        run = subprocess.run(
            [sys.executable , script,csv_file],
            capture_output=True,
            text=True
        )
        return run.stdout


    def executor_agent(self, state: State):
        llm_with_tool = llm.bind_tools([self.execute_code],tool_choice="execute_code")

        messages = [
            SystemMessage(
                content="""
                Your job is to run the CSV script using the provided tool.
                Do NOT analyze or modify the data in any way.
                Just execute the script and return its output exactly as it is.
                USE THE TOOL GIVEN TO EXECUTE CODE
                """
            ),
            HumanMessage(
                content=f"Please run the CSV script on this file: {state['csv_file']}"
            )
        ]

        result = llm_with_tool.invoke(messages)

        return {
        "messages": [result],
        "output": result.content
    }
    def analyser_agent(self,state : State):
        user_msg = (
        "Your work is to analyse the CSV output and suggest all possible charts "
        "with column names in a neat, structured format. "
        "Previous output:\n" + state['messages'][-1].content
    )
        analysis = llm.invoke([HumanMessage(content=user_msg)])
        return {
            "messages" : [analysis],
            "output" : analysis.content
        }
    def html_converter_agent(self,state : State):
        llm_with_tools = llm.bind_tools([File_Output])
        user_msg = (
            f"""Your Work is to convert the analysed content into  
            well designed with more colours bold and all and very very attractive atteactive html structure and also short para which is readable
              and use File_Output tool 
            to write the content inside the html file and after the content is {state['messages'][-1].content}
            """
        )
        html_ = llm_with_tools.invoke([HumanMessage(
            content=user_msg
        )])

        return {
            "messages" : [html_],
            "output" : html_.content
        }

    def _build_graph(self): 
        tool_node2 = ToolNode([File_Output])
        tool_node1 = ToolNode([self.execute_code])
        graph_builder = StateGraph(self.State)
        graph_builder.add_node("executor agent", self.executor_agent)
        graph_builder.add_node("analyser agent" , self.analyser_agent)
        graph_builder.add_node("html agent",self.html_converter_agent)
        graph_builder.add_node("tools" , tool_node1)
        graph_builder.add_node("html tool",tool_node2)
        graph_builder.add_edge(START , "executor agent")
        graph_builder.add_conditional_edges("executor agent" , tools_condition)
        graph_builder.add_edge("tools" , "analyser agent")
        graph_builder.add_edge("analyser agent" , "html agent")
        graph_builder.add_edge("html agent", "html tool")
        graph_builder.add_edge("html tool", END)
        return graph_builder.compile()
    def invoke(self,state):
        return self.graph.invoke(state)
        
