import gradio as gr
import os
from graph import Graph
import shutil
UPLOADED = "uploaded_files"
os.makedirs(UPLOADED,exist_ok=True)

def save_(file):
    file_name = os.path.basename(file)
    dest_path = os.path.join(UPLOADED , file_name)
    shutil.copy(file, dest_path)
    graph = Graph()
    result = graph.invoke({
        "messages" : [],
        "csv_file" :dest_path,
        "output" : ""
    })
    return result["messages"][-1]

app = gr.Interface(
    fn=save_,
    inputs=gr.File(file_types=[".csv"]),
    outputs="text"
)

app.launch()