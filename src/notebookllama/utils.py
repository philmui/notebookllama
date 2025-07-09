from dotenv import load_dotenv
import pandas as pd
import json
import os
import uuid
import warnings
import tempfile as tmp
from datetime import datetime

from mrkdwn_analysis import MarkdownAnalyzer
from pydantic import BaseModel, Field, model_validator
from llama_index.core.llms import ChatMessage
from llama_cloud_services import LlamaExtract, LlamaParse
from llama_cloud_services.extract import SourceText
from llama_cloud.client import AsyncLlamaCloud
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.base.response.schema import Response
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.llms.openai import OpenAIResponses
from typing import List, Tuple, Union, Optional, Dict, cast
from typing_extensions import Self
from pyvis.network import Network

load_dotenv()


class Node(BaseModel):
    id: str
    content: str


class Edge(BaseModel):
    from_id: str
    to_id: str


class MindMap(BaseModel):
    nodes: List[Node] = Field(
        description="List of nodes in the mind map, each represented as a Node object with an 'id' and concise 'content' (no more than 5 words).",
        examples=[
            [
                Node(id="A", content="Fall of the Roman Empire"),
                Node(id="B", content="476 AD"),
                Node(id="C", content="Barbarian invasions"),
            ],
            [
                Node(id="A", content="Auxin is released"),
                Node(id="B", content="Travels to the roots"),
                Node(id="C", content="Root cells grow"),
            ],
        ],
    )
    edges: List[Edge] = Field(
        description="The edges connecting the nodes of the mind map, as a list of Edge objects with from_id and to_id fields representing the source and target node IDs.",
        examples=[
            [
                Edge(from_id="A", to_id="B"),
                Edge(from_id="A", to_id="C"),
                Edge(from_id="B", to_id="C"),
            ],
            [
                Edge(from_id="C", to_id="A"),
                Edge(from_id="B", to_id="C"),
                Edge(from_id="A", to_id="B"),
            ],
        ],
    )

    @model_validator(mode="after")
    def validate_mind_map(self) -> Self:
        all_nodes = [el.id for el in self.nodes]
        all_edges = [el.from_id for el in self.edges] + [el.to_id for el in self.edges]
        if set(all_nodes).issubset(set(all_edges)) and set(all_nodes) != set(all_edges):
            raise ValueError(
                "There are non-existing nodes listed as source or target in the edges"
            )
        return self


class MindMapCreationFailedWarning(Warning):
    """A warning returned if the mind map creation failed"""


class ClaimVerification(BaseModel):
    claim_is_true: bool = Field(
        description="Based on the provided sources information, the claim passes or not."
    )
    supporting_citations: Optional[List[str]] = Field(
        description="A minimum of one and a maximum of three citations from the sources supporting the claim. If the claim is not supported, please leave empty",
        default=None,
        min_length=1,
        max_length=3,
    )

    @model_validator(mode="after")
    def validate_claim_ver(self) -> Self:
        if not self.claim_is_true and self.supporting_citations is not None:
            self.supporting_citations = ["The claim was deemed false."]
        return self


if (
    os.getenv("LLAMACLOUD_API_KEY", None)
    and os.getenv("EXTRACT_AGENT_ID", None)
    and os.getenv("LLAMACLOUD_PIPELINE_ID", None)
    and os.getenv("OPENAI_API_KEY", None)
):
    LLM = OpenAIResponses(model="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY"))
    CLIENT = AsyncLlamaCloud(token=os.getenv("LLAMACLOUD_API_KEY"))
    EXTRACT_AGENT = LlamaExtract(api_key=os.getenv("LLAMACLOUD_API_KEY")).get_agent(
        id=os.getenv("EXTRACT_AGENT_ID")
    )
    PARSER = LlamaParse(api_key=os.getenv("LLAMACLOUD_API_KEY"), result_type="markdown")
    PIPELINE_ID = os.getenv("LLAMACLOUD_PIPELINE_ID")
    RETR = LlamaCloudIndex(
        api_key=os.getenv("LLAMACLOUD_API_KEY"), pipeline_id=PIPELINE_ID
    ).as_retriever()
    QE = CitationQueryEngine(
        retriever=RETR,
        llm=LLM,
        citation_chunk_size=256,
        citation_chunk_overlap=50,
    )
    LLM_STRUCT = LLM.as_structured_llm(MindMap)
    LLM_VERIFIER = LLM.as_structured_llm(ClaimVerification)


def md_table_to_pd_dataframe(md_table: Dict[str, list]) -> Optional[pd.DataFrame]:
    try:
        df = pd.DataFrame()
        for i in range(len(md_table["header"])):
            ls = [row[i] for row in md_table["rows"]]
            df[md_table["header"][i]] = ls
        return df
    except Exception as e:
        warnings.warn(f"Skipping table as an error occurred: {e}")
        return None


async def parse_file(
    file_path: str, with_images: bool = False, with_tables: bool = False
) -> Union[Tuple[Optional[str], Optional[List[str]], Optional[List[pd.DataFrame]]]]:
    images: Optional[List[str]] = None
    text: Optional[str] = None
    tables: Optional[List[pd.DataFrame]] = None
    document = await PARSER.aparse(file_path=file_path)
    md_content = await document.aget_markdown_documents()
    if len(md_content) != 0:
        text = "\n\n---\n\n".join([doc.text for doc in md_content])
    if with_images:
        if os.path.exists("static/") and len(os.listdir("static/")) >= 0:
            for image_file in os.listdir("static/"):
                image_path = os.path.join("static/", image_file)
                if os.path.isfile(image_path) and "_at_" not in image_path:
                    with open(image_path, "rb") as img:
                        bts = img.read()
                    with open(
                        os.path.splitext(image_path)[0].replace("_current", "")
                        + f"_at_{datetime.now().strftime('%Y_%d_%m_%H_%M_%S_%f')[:-3]}.png",
                        "wb",
                    ) as img_tw:
                        img_tw.write(bts)
                    os.remove(image_path)
        images = await document.asave_all_images("static/")
        for image in images:
            with open(image, "rb") as rb:
                bts = rb.read()
            with open(os.path.splitext(image)[0] + "_current.png", "wb") as wb:
                wb.write(bts)
            os.remove(image)
    if with_tables:
        if text is not None:
            tmp_file = tmp.NamedTemporaryFile(
                suffix=".md", delete=False, delete_on_close=False
            )
            with open(tmp_file.name, "w") as f:
                f.write(text)
            analyzer = MarkdownAnalyzer(tmp_file.name)
            md_tables = analyzer.identify_tables()["Table"]
            tables = []
            for md_table in md_tables:
                table = md_table_to_pd_dataframe(md_table=md_table)
                if table is not None:
                    tables.append(table)
                    os.makedirs("data/extracted_tables/", exist_ok=True)
                    table.to_csv(
                        f"data/extracted_tables/table_{datetime.now().strftime('%Y_%d_%m_%H_%M_%S_%f')[:-3]}.csv",
                        index=False,
                    )
        os.remove(tmp_file.name)
    return text, images, tables


async def process_file(
    filename: str,
) -> Union[Tuple[str, None], Tuple[None, None], Tuple[str, str]]:
    with open(filename, "rb") as f:
        file = await CLIENT.files.upload_file(upload_file=f)
    files = [{"file_id": file.id}]
    await CLIENT.pipelines.add_files_to_pipeline_api(
        pipeline_id=PIPELINE_ID, request=files
    )
    text, _, _ = await parse_file(file_path=filename)
    if text is None:
        return None, None
    extraction_output = await EXTRACT_AGENT.aextract(
        files=SourceText(text_content=text, filename=file.name)
    )
    if extraction_output:
        return json.dumps(extraction_output.data, indent=4), text
    return None, None


async def get_mind_map(summary: str, highlights: List[str]) -> Union[str, None]:
    try:
        keypoints = "\n- ".join(highlights)
        messages = [
            ChatMessage(
                role="user",
                content=f"This is the summary for my document: {summary}\n\nAnd these are the key points:\n- {keypoints}",
            )
        ]
        response = await LLM_STRUCT.achat(messages=messages)
        response_json = json.loads(response.message.content)
        net = Network(directed=True, height="750px", width="100%")
        net.set_options("""
            var options = {
            "physics": {
                "enabled": false
            }
            }
            """)
        nodes = response_json["nodes"]
        edges = response_json["edges"]
        for node in nodes:
            net.add_node(n_id=node["id"], label=node["content"])
        for edge in edges:
            net.add_edge(source=edge["from_id"], to=edge["to_id"])
        name = str(uuid.uuid4())
        net.save_graph(name + ".html")
        return name + ".html"
    except Exception as e:
        warnings.warn(
            message=f"An error occurred during the creation of the mind map: {e}",
            category=MindMapCreationFailedWarning,
        )
        return None


async def query_index(question: str) -> Union[str, None]:
    response = await QE.aquery(question)
    response = cast(Response, response)
    sources = []
    if not response.response:
        return None
    if response.source_nodes is not None:
        sources = [node.text for node in response.source_nodes]
    return (
        "## Answer\n\n"
        + response.response
        + "\n\n## Sources\n\n- "
        + "\n- ".join(sources)
    )


async def get_plots_and_tables(
    file_path: str,
) -> Union[Tuple[Optional[List[str]], Optional[List[pd.DataFrame]]]]:
    _, images, tables = await parse_file(
        file_path=file_path, with_images=True, with_tables=True
    )
    return images, tables


def verify_claim(
    claim: str,
    sources: str,
) -> Tuple[bool, Optional[List[str]]]:
    response = LLM_VERIFIER.chat(
        [
            ChatMessage(
                role="user",
                content=f"I have this claim: {claim} that is allegedgly supported by these sources:\n\n'''\n{sources}\n'''\n\nCan you please tell me whether or not this claim is thrutful and, if it is, identify one to three passages in the sources specifically supporting the claim?",
            )
        ]
    )
    response_json = json.loads(response.message.content)
    return response_json["claim_is_true"], response_json["supporting_citations"]
