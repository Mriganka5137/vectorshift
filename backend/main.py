from fastapi import FastAPI, Form
from pydantic import BaseModel
import networkx as nx
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PipelineData(BaseModel):
    pipeline: str

@app.get('/')
def read_root():
    return {"Hello": "World"}

@app.post('/pipelines/parse')
async def parse_pipeline(pipeline_data: PipelineData):
    try:
        # Parse the JSON string into a Python dictionary
        pipeline = json.loads(pipeline_data.pipeline)
        
        # Validate pipeline structure
        if 'nodes' not in pipeline or 'edges' not in pipeline:
            return {"error": "Invalid pipeline structure"}

        # Create a directed graph
        G = nx.DiGraph()

        # Add nodes and edges to the graph
        for node in pipeline['nodes']:
            if 'id' not in node:
                return {"error": "Node missing 'id' field"}
            G.add_node(node['id'])

        for edge in pipeline['edges']:
            if 'source' not in edge or 'target' not in edge:
                return {"error": "Edge missing 'source' or 'target' field"}
            G.add_edge(edge['source'], edge['target'])

        # Calculate the number of nodes and edges
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()

        # Check if the graph is a DAG
        is_dag = nx.is_directed_acyclic_graph(G)

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "is_dag": is_dag
        }
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}
    except KeyError:
        return {"error": "Invalid pipeline structure"}
    except Exception as e:
        return {"error": str(e)}
