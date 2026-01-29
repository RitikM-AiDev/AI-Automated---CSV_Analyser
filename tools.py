from langchain_core.tools import tool
import os
import sys
import subprocess
@tool 
def File_Output(html_content :str):
    """Write html content into chart.html"""
    with open("chart.html","w",encoding="utf-8") as file:
        file.write(html_content)
    runner_tool(html_content)
    return "content written"

def runner_tool(html_content :str):
    """After Writing the content running in"""
    run = subprocess.run(["cmd","/c","start","chart.html"])
    return {
        "output" : html_content
    }