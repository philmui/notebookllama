import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure OpenTelemetry at SDK level BEFORE any imports
ENABLE_OBSERVABILITY = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"

if not ENABLE_OBSERVABILITY:
    # Disable OpenTelemetry at SDK level
    os.environ["OTEL_TRACES_SAMPLER"] = "off"
    os.environ["OTEL_TRACES_EXPORTER"] = "none"
    os.environ["OTEL_METRICS_EXPORTER"] = "none"
    os.environ["OTEL_LOGS_EXPORTER"] = "none"
    print("📊 OpenTelemetry disabled at SDK level (server)")
else:
    print("📊 OpenTelemetry enabled (server)")

from querying import query_index
from processing import process_file
from mindmap import get_mind_map
from fastmcp import FastMCP
from typing import List, Union, Literal

mcp: FastMCP = FastMCP(name="MCP For NotebookLM")


@mcp.tool(
    name="process_file_tool",
    description="This tool is useful to process files and produce summaries, question-answers and highlights.",
)
async def process_file_tool(
    filename: str,
) -> Union[str, Literal["Sorry, your file could not be processed."]]:
    notebook_model, text = await process_file(filename=filename)
    if notebook_model is None:
        return "Sorry, your file could not be processed."
    if text is None:
        text = ""
    return notebook_model + "\n%separator%\n" + text


@mcp.tool(name="get_mind_map_tool", description="This tool is useful to get a mind ")
async def get_mind_map_tool(
    summary: str, highlights: List[str]
) -> Union[str, Literal["Sorry, mind map creation failed."]]:
    mind_map_fl = await get_mind_map(summary=summary, highlights=highlights)
    if mind_map_fl is None:
        return "Sorry, mind map creation failed."
    return mind_map_fl


@mcp.tool(name="query_index_tool", description="Query a LlamaCloud index.")
async def query_index_tool(question: str) -> str:
    response = await query_index(question=question)
    if response is None:
        return "Sorry, I was unable to find an answer to your question."
    return response


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
