# NotebookLlaMa🦙

## A fluffy and open-source alternative to NotebookLM!

https://github.com/user-attachments/assets/7e9cca45-8a4c-4dfa-98d2-2cef147422f2

This project is aimed at producing a fully open-source, [**LlamaCloud**](https://cloud.llamaindex.ai?utm_source=demo&utm_medium=notebookLM)-backed alternative to NotebookLM.

### Prerequisites

This project uses `uv` to manage dependencies. Before you begin, make sure you have `uv` installed.

On macOS and Linux:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For more install options, see `uv`'s [official documentation](https://docs.astral.sh/uv/getting-started/installation/).

### Get it up and running!

Get the GitHub repository:

```bash
git clone https://github.com/run-llama/notebookllama
```

Install dependencies:

```bash
cd notebookllama/
uv sync
```

Modify the `.env.example` file with your API keys:

- `OPENAI_API_KEY`: find it [on OpenAI Platform](https://platform.openai.com/api-keys)
- `ELEVENLABS_API_KEY`: find it [on ElevenLabs Settings](https://elevenlabs.io/app/settings/api-keys)
- `LLAMACLOUD_API_KEY`: find it [on LlamaCloud Dashboard](https://cloud.llamaindex.ai?utm_source=demo&utm_medium=notebookLM)

Rename the file to `.env`:

```bash
mv .env.example .env
```

Now, you will have to execute the following scripts:

```bash
uv run tools/create_llama_extract_agent.py
uv run tools/create_llama_cloud_index.py
```

And you're ready to set up the app!

Launch Postgres and Jaeger:

```bash
docker compose up -d
```

Run the **MCP** server:

```bash
uv run src/notebookllama/server.py
```

Now, launch the Streamlit app:

```bash
streamlit run src/notebookllama/Home.py
```

> [!IMPORTANT]
>
> _You might need to install `ffmpeg` if you do not have it installed already_

And start exploring the app at `http://localhost:8501/`.

### Contributing

Contribute to this project following the [guidelines](./CONTRIBUTING.md).

### License

This project is provided under an [MIT License](LICENSE).
