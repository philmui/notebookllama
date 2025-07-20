# Mind Map Generation with `mindmap.py`

This document provides a detailed explanation of the `src/notebookllama/mindmap.py` module. Its purpose is to automatically generate interactive, visual mind maps from document summaries using a Large Language Model (LLM).

We will cover:
1.  **How it Works**: A deep dive into the code and the concepts behind it.
2.  **How to Use `get_mind_map`**: A practical guide with code examples.
3.  **Alternative Approaches**: A comparison with Knowledge Graphs and Property Graphs in LlamaIndex.
4.  **Extensions and Next Steps**: Ideas for enhancing this functionality.

## Table of Contents

- [Mind Map Generation with `mindmap.py`](#mind-map-generation-with-mindmappy)
  - [Table of Contents](#table-of-contents)
  - [1. How it Works: A Deep Dive](#1-how-it-works-a-deep-dive)
    - [The Core Idea: Structured LLM Output](#the-core-idea-structured-llm-output)
    - [Defining the Structure: `Node`, `Edge`, and `MindMap`](#defining-the-structure-node-edge-and-mindmap)
    - [The `get_mind_map` Function: Step-by-Step](#the-get_mind_map-function-step-by-step)
  - [2. How to Use `get_mind_map`](#2-how-to-use-get_mind_map)
    - [Example](#example)
  - [3. Alternative Approaches: Knowledge Graphs](#3-alternative-approaches-knowledge-graphs)
    - [Example Comparison](#example-comparison)
  - [4. Extensions and Next Steps](#4-extensions-and-next-steps)

## 1. How it Works: A Deep Dive

The core idea behind `mindmap.py` is to leverage an LLM's ability to understand text and structure information, and then use that structured information to generate a visual graph. This process can be broken down into two main parts: getting structured data from an LLM, and then visualizing that data.

### The Core Idea: Structured LLM Output

Normally, an LLM outputs unstructured text. However, by providing a specific schema (a "template" for the output), we can compel the LLM to return a response that conforms to our desired structure, such as a JSON object. This is a powerful feature of libraries like LlamaIndex.

`mindmap.py` uses this technique to ask the LLM to read a summary and return a list of concepts (nodes) and the connections between them (edges).

### Defining the Structure: `Node`, `Edge`, and `MindMap`

To get a structured response, we first need to define the structure. This is done using Pydantic, a data validation library. `mindmap.py` defines three `BaseModel` classes:

*   `Node`: Represents a single concept or idea in the mind map. It has a unique `id` and a short `content` description.
*   `Edge`: Represents a directed connection between two nodes, specified by their IDs (`from_id` and `to_id`).
*   `MindMap`: The main container object that the LLM is tasked with creating. It holds the complete list of `nodes` and `edges`.

```python
class Node(BaseModel):
    id: str
    content: str

class Edge(BaseModel):
    from_id: str
    to_id: str

class MindMap(BaseModel):
    nodes: List[Node] = Field(
        description="List of nodes in the mind map...",
        examples=[...]
    )
    edges: List[Edge] = Field(
        description="The edges connecting the nodes...",
        examples=[...]
    )
```

The `description` and `examples` within `Field` are crucial. They are passed to the LLM as part of the system prompt, giving it clear instructions and examples of what a valid output looks like. This significantly increases the reliability of the LLM's output.

### The `get_mind_map` Function: Step-by-Step

This asynchronous function orchestrates the entire process from prompting the LLM to saving the final visualization.

1.  **Prompting the LLM**: The function takes a document `summary` and a list of `highlights` and combines them into a single, clear prompt. This prompt essentially asks the LLM, "Based on the following text, create a mind map."

2.  **Invoking the Structured LLM**: It uses a LlamaIndex `OpenAIResponses` LLM that has been configured to output data matching the `MindMap` Pydantic model.
    ```python
    LLM_STRUCT = LLM.as_structured_llm(MindMap)
    response = await LLM_STRUCT.achat(messages=messages)
    ```
    When this code is executed, LlamaIndex internally modifies the prompt to instruct the LLM to generate a JSON object that adheres to the `MindMap` schema.

3.  **Receiving and Parsing the Response**: The `response` from the LLM contains the generated mind map as a JSON string. This is parsed into a Python dictionary.

4.  **Visualization with `pyvis`**: The script then uses the `pyvis` library to build the interactive visualization. It iterates through the nodes and edges from the LLM's response and adds them to a `Network` object.
    ```python
    net = Network(directed=True, height="750px", width="100%")
    # ...
    for node in nodes:
        net.add_node(n_id=node["id"], label=node["content"])
    for edge in edges:
        net.add_edge(source=edge["from_id"], to=edge["to_id"])
    ```

5.  **Saving and Returning**: The `pyvis` network is saved as a self-contained HTML file with a unique name. The function returns the path to this file, which can then be displayed in a web browser or embedded in a web application. If any step fails, it returns `None`.

## 2. How to Use `get_mind_map`

Using the function is straightforward. You need an `async` environment to call it. Provide a summary string and a list of highlight strings.

### Example

Here is a complete, runnable example:

```python
import asyncio
import os
from notebookllama.mindmap import get_mind_map

# Ensure your OPENAI_API_KEY is set as an environment variable
# os.environ["OPENAI_API_KEY"] = "sk-..."

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY environment variable not set. Aborting.")
        return

    summary = "The solar system is a gravitationally bound system comprising the Sun and the objects that orbit it. The largest objects are the eight planets, in order from the Sun: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune."
    highlights = [
        "Solar system is bound by gravity",
        "Sun is at the center",
        "There are eight planets",
        "Planets orbit the sun"
    ]

    print("Generating mind map...")
    html_file = await get_mind_map(summary, highlights)

    if html_file:
        print(f"Mind map generated successfully! Open this file in your browser: {html_file}")
    else:
        print("Failed to generate mind map. Check for warnings in the console.")

if __name__ == "__main__":
    asyncio.run(main())
```

When you run this script, it will call the OpenAI API and generate an HTML file (e.g., `a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.html`) in your project's root directory. Opening this file will show an interactive graph where you can drag the nodes around.

## 3. Alternative Approaches: Knowledge Graphs

The `mindmap.py` approach is excellent for flexible, high-level visualization. However, LlamaIndex offers more structured and powerful graph-based tools for knowledge representation, primarily **Knowledge Graphs** and **Property Graphs**.

Let's compare them.

| Feature         | `mindmap.py` (Current)                                   | `KnowledgeGraphIndex` (LlamaIndex)                     | `PropertyGraph` (LlamaIndex Integrations)                 |
| --------------- | -------------------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------- |
| **Basic Unit**  | Node with a label and an untyped edge.                   | Triplet: `(Subject, Predicate, Object)`                | Nodes and Edges with arbitrary properties (key-value pairs). |
| **Structure**   | Flexible, hierarchical, visually-oriented.               | Rigid, semantic, based on factual triplets.            | Highly flexible and rich. Models complex data.          |
| **Generation**  | Generated by LLM from a summary.                         | Extracted by LLM from source documents directly.       | Extracted by LLM, mapping entities to nodes/properties. |
| **Use Case**    | High-level concept summarization and visualization.      | Building a queryable database of facts.                | Modeling complex domains with rich metadata.            |

### Example Comparison

Let's use the sentence: "Elon Musk founded SpaceX in 2002."

*   **`mindmap.py` Output:**
    *   Node A: "Elon Musk"
    *   Node B: "SpaceX"
    *   Node C: "Founded in 2002"
    *   Edge: A -> B
    *   Edge: B -> C

*   **`KnowledgeGraphIndex` Output:**
    *   Triplet: (`Elon Musk`, `founded`, `SpaceX`)
    *   Triplet: (`SpaceX`, `founded on`, `2002`)

*   **`PropertyGraph` Output:**
    *   **Node**: `label="Person", properties={"name": "Elon Musk"}`
    *   **Node**: `label="Company", properties={"name": "SpaceX", "founded_year": 2002}`
    *   **Relationship**: `type="FOUNDED"` connecting the Person node to the Company node.

**Conclusion**: The current `mindmap.py` script is a lightweight "visual graph" generator. `KnowledgeGraphIndex` is a step up for structured Q&A, and Property Graphs offer the most power and flexibility for modeling complex systems, often requiring a dedicated graph database like Neo4j.

## 4. Extensions and Next Steps

This mind-mapping tool provides a solid foundation. Here are several ways it could be extended:

1.  **Property-Rich Nodes**: Evolve the `Node` model to include more properties, such as `type` (e.g., 'Concept', 'Date', 'Person'), a longer `description`, or a color. This would allow for more visually informative maps (e.g., all 'Date' nodes are green).

2.  **Multi-Document Synthesis**: Modify the process to accept summaries and highlights from several documents at once. This would enable the creation of a single, synthesized mind map covering an entire topic or project.

3.  **Graph-based Q&A**: The generated graph, while simple, could be used to answer basic questions. One could load the nodes and edges into a LlamaIndex `GraphIndex` to answer queries like, "What concepts are related to 'Barbarian Invasions'?"

4.  **Integration with RAG (Retrieval-Augmented Generation)**: The mind map could serve as a "table of contents" for a RAG system. A user's query could first be used to find the most relevant node(s) in the graph. Then, the content of those nodes could be used to retrieve more specific, detailed text chunks from the original source documents for a more accurate answer.

5.  **Interactive UI**: The `pyvis` output is interactive, but the data flow is one-way. A more advanced implementation could allow users to edit the graph in the UI (add/remove/change nodes) and have those changes be saved or used to trigger further actions.

6.  **Alternative Layouts**: Expose more of the `pyvis` physics and layout options to the user, allowing them to switch between hierarchical, force-directed, and other layouts to best view the information. 