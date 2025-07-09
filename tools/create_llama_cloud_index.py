import os
from dotenv import load_dotenv

from cli.utils import (
    DefaultOrCustomApp,
    SelectEmbeddingApp,
    AzureEmbeddingApp,
    GeminiEmbeddingApp,
    BedrockEmbeddingApp,
    OtherEmbeddingApp,
)
from llama_cloud import (
    PipelineCreateEmbeddingConfig_OpenaiEmbedding,
    PipelineCreateEmbeddingConfig_AzureEmbedding,
    PipelineCreateEmbeddingConfig_BedrockEmbedding,
    PipelineCreateEmbeddingConfig_CohereEmbedding,
    PipelineCreateEmbeddingConfig_GeminiEmbedding,
    PipelineCreateEmbeddingConfig_HuggingfaceApiEmbedding,
    PipelineTransformConfig_Advanced,
    AdvancedModeTransformConfigChunkingConfig_Sentence,
    AdvancedModeTransformConfigSegmentationConfig_Page,
    PipelineCreate,
)
from llama_cloud.client import LlamaCloud
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.azure_inference import AzureAIEmbeddingsModel
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.embeddings.bedrock import BedrockEmbedding


def default(client: LlamaCloud):
    load_dotenv()

    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY")
    )

    embedding_config = PipelineCreateEmbeddingConfig_OpenaiEmbedding(
        type="OPENAI_EMBEDDING",
        component=embed_model,
    )
    segm_config = AdvancedModeTransformConfigSegmentationConfig_Page(mode="page")
    chunk_config = AdvancedModeTransformConfigChunkingConfig_Sentence(
        chunk_size=1024,
        chunk_overlap=200,
        separator="<whitespace>",
        paragraph_separator="\n\n\n",
        mode="sentence",
    )

    transform_config = PipelineTransformConfig_Advanced(
        segmentation_config=segm_config,
        chunking_config=chunk_config,
        mode="advanced",
    )

    pipeline_request = PipelineCreate(
        name="notebooklm_pipeline",
        embedding_config=embedding_config,
        transform_config=transform_config,
    )

    pipeline = client.pipelines.upsert_pipeline(request=pipeline_request)

    with open(".env", "a") as f:
        f.write(f'\nLLAMACLOUD_PIPELINE_ID="{pipeline.id}"')

    return 0


def main():
    load_dotenv()
    client = LlamaCloud(token=os.getenv("LLAMACLOUD_API_KEY"))
    app1 = DefaultOrCustomApp()
    app1.run()

    if app1.title == "With Default Settings":
        default(client=client)
        return 0
    else:
        app2 = SelectEmbeddingApp()
        app2.run()

        if app2.title == "Azure":
            app3 = AzureEmbeddingApp()
            app3.run()
            api_key = app3.form_data.get("api_key", "")
            endpoint = app3.form_data.get("target_uri", "")
            embed_model = AzureAIEmbeddingsModel(credential=api_key, endpoint=endpoint)
            embedding_config = PipelineCreateEmbeddingConfig_AzureEmbedding(
                type="AZURE_EMBEDDING",
                component=embed_model,
            )

        elif app2.title == "Bedrock":
            app4 = BedrockEmbeddingApp()
            app4.run()
            api_key = app4.form_data.get("api_key", "")
            key_id = app4.form_data.get("key_id", "")
            region = app4.form_data.get("region", "")
            model = app4.form_data.get("model", "")
            embed_model = BedrockEmbedding(
                model_name=model,
                aws_access_key_id=key_id,
                aws_secret_access_key=api_key,
                region_name=region,
            )
            embedding_config = PipelineCreateEmbeddingConfig_BedrockEmbedding(
                type="BEDROCK_EMBEDDING",
                component=embed_model,
            )

        elif app2.title == "Gemini":
            app5 = GeminiEmbeddingApp()
            app5.run()
            api_key = app5.form_data.get("api_key", "")
            embed_model = GeminiEmbedding(api_key=api_key)
            embedding_config = PipelineCreateEmbeddingConfig_GeminiEmbedding(
                type="GEMINI_EMBEDDING",
                component=embed_model,
            )

        else:
            app6 = OtherEmbeddingApp()
            app6.run()
            api_key = app6.form_data.get("api_key", "")
            model = app6.form_data.get("model", "")
            if app2.title == "Cohere":
                embed_model = CohereEmbedding(
                    model_name=model, api_key=api_key, cohere_api_key=api_key
                )
                embedding_config = PipelineCreateEmbeddingConfig_CohereEmbedding(
                    type="COHERE_EMBEDDING",
                    component=embed_model,
                )
            elif app2.title == "OpenAI":
                embed_model = OpenAIEmbedding(model=model, api_key=api_key)
                embedding_config = PipelineCreateEmbeddingConfig_OpenaiEmbedding(
                    type="OPENAI_EMBEDDING",
                    component=embed_model,
                )
            else:
                embed_model = HuggingFaceInferenceAPIEmbedding(
                    token=api_key, model_name=model
                )
                embedding_config = (
                    PipelineCreateEmbeddingConfig_HuggingfaceApiEmbedding(
                        type="HUGGINGFACE_API_EMBEDDING",
                        component=embed_model,
                    )
                )
    segm_config = AdvancedModeTransformConfigSegmentationConfig_Page(mode="page")
    chunk_config = AdvancedModeTransformConfigChunkingConfig_Sentence(
        chunk_size=1024,
        chunk_overlap=200,
        separator="<whitespace>",
        paragraph_separator="\n\n\n",
        mode="sentence",
    )

    transform_config = PipelineTransformConfig_Advanced(
        segmentation_config=segm_config,
        chunking_config=chunk_config,
        mode="advanced",
    )

    pipeline_request = PipelineCreate(
        name="notebooklm_pipeline",
        embedding_config=embedding_config,
        transform_config=transform_config,
    )

    pipeline = client.pipelines.upsert_pipeline(request=pipeline_request)

    with open(".env", "a") as f:
        f.write(f'\nLLAMACLOUD_PIPELINE_ID="{pipeline.id}"')

    return 0


if __name__ == "__main__":
    main()
