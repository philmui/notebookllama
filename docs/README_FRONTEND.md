# Streamlit Frontend Architecture & MCP Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [Frontend Architecture](#frontend-architecture)
3. [Streamlit App Deep Dive](#streamlit-app-deep-dive)
4. [MCP Integration Layer](#mcp-integration-layer)
5. [User Interface Components](#user-interface-components)
6. [Workflow Execution](#workflow-execution)
7. [Session State Management](#session-state-management)
8. [File Processing Pipeline](#file-processing-pipeline)
9. [Audio Generation](#audio-generation)
10. [Error Handling](#error-handling)
11. [Configuration & Environment](#configuration--environment)
12. [Development Guide](#development-guide)

## Overview

The **Streamlit Frontend** (`src/notebookllama/Home.py`) serves as the primary user interface for NotebookLlaMa, providing an intuitive web-based interface for document processing, mind map generation, and audio podcast creation. The frontend orchestrates complex workflows by communicating with the MCP server backend through a sophisticated workflow engine.

### Key Features

- **Document Upload & Processing**: PDF file upload with automatic processing
- **Interactive Results Display**: Summary, highlights, Q&A, and mind maps
- **Audio Podcast Generation**: AI-powered conversation generation
- **Session Management**: Persistent state across user interactions
- **Real-time Feedback**: Progress indicators and error handling
- **Responsive Design**: Adaptive layout for different screen sizes

### Core Components

```mermaid
graph TB
    subgraph "Streamlit Frontend"
        A[Home.py Main App]
        B[File Upload Handler]
        C[UI Components]
        D[Session State]
        E[Workflow Orchestrator]
    end
    
    subgraph "Workflow Engine"
        F[NotebookLMWorkflow]
        G[FileInputEvent]
        H[NotebookOutputEvent]
        I[Step Functions]
    end
    
    subgraph "MCP Communication"
        J[BasicMCPClient]
        K[HTTP Requests]
        L[Tool Calls]
    end
    
    subgraph "MCP Server Backend"
        M[FastMCP Server]
        N[Tool Registry]
        O[process_file_tool]
        P[get_mind_map_tool]
        Q[query_index_tool]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    E --> F
    F --> G
    F --> H
    F --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    N --> P
    N --> Q
```

## Frontend Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        A[Streamlit Web App]
        B[File Upload Widget]
        C[Document Title Input]
        D[Process Document Button]
        E[Results Display Area]
        F[Podcast Configuration]
        G[Audio Generation Button]
    end
    
    subgraph "Application Logic Layer"
        H[Session State Manager]
        I[File Handler]
        J[Workflow Coordinator]
        K[Error Handler]
        L[Audio Processor]
    end
    
    subgraph "Integration Layer"
        M[Async Workflow Runner]
        N[Sync Workflow Wrapper]
        O[Event Loop Manager]
    end
    
    subgraph "Backend Communication"
        P[Workflow Engine]
        Q[MCP Client]
        R[HTTP Transport]
    end
    
    subgraph "External Services"
        S[MCP Server]
        T[LlamaCloud]
        U[OpenAI]
        V[ElevenLabs]
        W[PostgreSQL]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    B --> H
    C --> H
    D --> I
    I --> J
    J --> K
    G --> L
    J --> M
    M --> N
    N --> O
    O --> P
    P --> Q
    Q --> R
    R --> S
    S --> T
    S --> U
    S --> V
    S --> W
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Session as Session State
    participant Workflow as Workflow Engine
    participant MCP as MCP Client
    participant Server as MCP Server
    participant Services as External Services
    
    User->>UI: Upload PDF File
    UI->>Session: Store file in session state
    UI->>User: Display file upload confirmation
    
    User->>UI: Enter document title
    UI->>Session: Update document_title
    
    User->>UI: Click "Process Document"
    UI->>Workflow: sync_run_workflow(file, title)
    Workflow->>Workflow: Create FileInputEvent
    Workflow->>MCP: call_tool(process_file_tool)
    MCP->>Server: HTTP POST /mcp/tools/process_file_tool
    Server->>Services: LlamaCloud Extract + Parse
    Services-->>Server: Extracted data + markdown
    Server-->>MCP: Tool response
    MCP-->>Workflow: Processed result
    Workflow->>Workflow: Parse into MindMapCreationEvent
    Workflow->>MCP: call_tool(get_mind_map_tool)
    MCP->>Server: HTTP POST /mcp/tools/get_mind_map_tool
    Server->>Services: OpenAI GPT-4 mind map generation
    Services-->>Server: Mind map HTML
    Server-->>MCP: Tool response
    MCP-->>Workflow: Mind map result
    Workflow->>Workflow: Create NotebookOutputEvent
    Workflow-->>UI: Complete workflow result
    UI->>Session: Store results in session state
    UI->>User: Display summary, highlights, Q&A, mind map
    
    User->>UI: Configure podcast settings
    UI->>Session: Store podcast configuration
    
    User->>UI: Click "Generate Podcast"
    UI->>Workflow: sync_create_podcast(content, config)
    Workflow->>Services: ElevenLabs audio generation
    Services-->>Workflow: Audio file
    Workflow-->>UI: Audio file path
    UI->>User: Display audio player
```

## Streamlit App Deep Dive

### Application Initialization

The Streamlit app follows a structured initialization process:

```python
# 1. Environment Configuration
load_dotenv()

# 2. OpenTelemetry Configuration
ENABLE_OBSERVABILITY = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"
if not ENABLE_OBSERVABILITY:
    os.environ["OTEL_TRACES_SAMPLER"] = "off"
    os.environ["OTEL_TRACES_EXPORTER"] = "none"
    os.environ["OTEL_METRICS_EXPORTER"] = "none"
    os.environ["OTEL_LOGS_EXPORTER"] = "none"

# 3. Service Initialization
engine_url = f"postgresql+psycopg2://{os.getenv('pgql_user')}:{os.getenv('pgql_psw')}@localhost:5432/{os.getenv('pgql_db')}"
sql_engine = OtelTracesSqlEngine(engine_url=engine_url, table_name="agent_traces", service_name="agent.traces")
document_manager = DocumentManager(engine_url=engine_url)

# 4. Workflow Initialization
WF = NotebookLMWorkflow(timeout=600)
```

### Page Configuration

```python
st.set_page_config(
    page_title="NotebookLlaMa - Home",
    page_icon="🏠",
    layout="wide",
    menu_items={
        "Get Help": "https://github.com/run-llama/notebooklm-clone/discussions/categories/general",
        "Report a bug": "https://github.com/run-llama/notebooklm-clone/issues/",
        "About": "An OSS alternative to NotebookLM that runs with the power of a flully Llama!",
    },
)
```

### Initialization Flow

```mermaid
flowchart TD
    A[App Startup] --> B[Load Environment Variables]
    B --> C[Configure OpenTelemetry]
    C --> D[Initialize Database Connections]
    D --> E[Initialize Workflow Engine]
    E --> F[Initialize Session State]
    F --> G[Setup UI Components]
    G --> H[Ready for User Interaction]
    
    subgraph "Environment Setup"
        B1[Load .env file]
        B2[Set API keys]
        B3[Configure database URL]
    end
    
    subgraph "Service Initialization"
        D1[SQL Engine]
        D2[Document Manager]
        D3[Observability]
    end
    
    subgraph "UI Setup"
        G1[Page Configuration]
        G2[Sidebar Setup]
        G3[Main Content Area]
    end
    
    B --> B1
    B --> B2
    B --> B3
    D --> D1
    D --> D2
    D --> D3
    G --> G1
    G --> G2
    G --> G3
```

## MCP Integration Layer

### Workflow Engine Integration

The Streamlit app integrates with the MCP server through a sophisticated workflow engine:

```python
# Workflow engine initialization
WF = NotebookLMWorkflow(timeout=600)

# Async workflow execution
async def run_workflow(file: io.BytesIO, document_title: str) -> Tuple[str, str, str, str, str]:
    # Create temporary file
    with temp.NamedTemporaryFile(suffix=".pdf", delete=False) as fl:
        content = file.getvalue()
        fl.write(content)
        fl.flush()
        temp_path = fl.name
    
    try:
        # Execute workflow
        ev = FileInputEvent(file=temp_path)
        result: NotebookOutputEvent = await WF.run(start_event=ev)
        
        # Process results
        q_and_a = ""
        for q, a in zip(result.questions, result.answers):
            q_and_a += f"**{q}**\n\n{a}\n\n"
        
        bullet_points = "## Bullet Points\n\n- " + "\n- ".join(result.highlights)
        
        # Handle mind map
        mind_map = result.mind_map
        if Path(mind_map).is_file():
            mind_map = read_html_file(mind_map)
            try:
                os.remove(result.mind_map)
            except OSError:
                pass
        
        return result.md_content, result.summary, q_and_a, bullet_points, mind_map
    finally:
        # Cleanup temporary file
        try:
            os.remove(temp_path)
        except OSError:
            await asyncio.sleep(0.1)
            try:
                os.remove(temp_path)
            except OSError:
                pass
```

### MCP Communication Architecture

```mermaid
graph TB
    subgraph "Streamlit App"
        A[User Interface]
        B[File Handler]
        C[Workflow Coordinator]
    end
    
    subgraph "Workflow Engine"
        D[NotebookLMWorkflow]
        E[FileInputEvent]
        F[NotebookOutputEvent]
        G[Step Functions]
    end
    
    subgraph "MCP Client Layer"
        H[BasicMCPClient]
        I[HTTP Transport]
        J[Tool Call Interface]
    end
    
    subgraph "MCP Server"
        K[FastMCP Server]
        L[Tool Registry]
        M[Request Handler]
    end
    
    subgraph "Tool Implementations"
        N[process_file_tool]
        O[get_mind_map_tool]
        P[query_index_tool]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    M --> O
    M --> P
```

### Tool Call Flow

```mermaid
sequenceDiagram
    participant UI as Streamlit UI
    participant WF as Workflow Engine
    participant MCP as MCP Client
    participant Server as MCP Server
    participant Tools as Tool Functions
    participant Services as External Services
    
    UI->>WF: sync_run_workflow(file, title)
    WF->>WF: Create FileInputEvent
    WF->>MCP: call_tool("process_file_tool", {filename})
    MCP->>Server: HTTP POST /mcp/tools/process_file_tool
    Server->>Tools: process_file_tool(filename)
    Tools->>Services: LlamaCloud Extract + Parse
    Services-->>Tools: Extracted data + markdown
    Tools-->>Server: JSON + %separator% + markdown
    Server-->>MCP: Tool response
    MCP-->>WF: Processed result
    WF->>WF: Parse result into MindMapCreationEvent
    WF->>MCP: call_tool("get_mind_map_tool", {summary, highlights})
    MCP->>Server: HTTP POST /mcp/tools/get_mind_map_tool
    Server->>Tools: get_mind_map_tool(summary, highlights)
    Tools->>Services: OpenAI GPT-4 mind map generation
    Services-->>Tools: Mind map HTML file
    Tools-->>Server: HTML file path
    Server-->>MCP: Tool response
    MCP-->>WF: Mind map result
    WF->>WF: Create NotebookOutputEvent
    WF-->>UI: Complete workflow result
```

## User Interface Components

### Main Interface Structure

```mermaid
graph TB
    subgraph "Streamlit Page Layout"
        A[Page Header]
        B[Sidebar]
        C[Main Content Area]
    end
    
    subgraph "Sidebar Components"
        D[Home Header]
        E[Navigation Info]
        F[Page Separator]
    end
    
    subgraph "Main Content"
        G[App Title]
        H[Document Title Input]
        I[File Upload Widget]
        J[Process Document Button]
        K[Results Display]
        L[Podcast Configuration]
        M[Audio Generation]
    end
    
    subgraph "Results Display"
        N[Summary Section]
        O[Bullet Points]
        P[FAQ Expander]
        Q[Mind Map]
        R[Podcast Config Panel]
    end
    
    A --> B
    A --> C
    B --> D
    B --> E
    B --> F
    C --> G
    C --> H
    C --> I
    C --> J
    C --> K
    C --> L
    C --> M
    K --> N
    K --> O
    K --> P
    K --> Q
    L --> R
```

### Document Title Management

```python
# Initialize session state for document title
if "document_title" not in st.session_state:
    st.session_state.document_title = randomname.get_name(
        adj=("music_theory", "geometry", "emotions"), 
        noun=("cats", "food")
    )

# Create text input with session state binding
document_title = st.text_input(
    label="Document Title",
    value=st.session_state.document_title,
    key="document_title_input",
)

# Update session state when input changes
if document_title != st.session_state.document_title:
    st.session_state.document_title = document_title
```

### File Upload Handler

```python
file_input = st.file_uploader(
    label="Upload your source PDF file!", 
    accept_multiple_files=False
)

if file_input is not None:
    # File is uploaded, show processing button
    if st.button("Process Document", type="primary"):
        with st.spinner("Processing document... This may take a few minutes."):
            try:
                # Execute workflow
                md_content, summary, q_and_a, bullet_points, mind_map = (
                    sync_run_workflow(file_input, st.session_state.document_title)
                )
                
                # Store results in session state
                st.session_state.workflow_results = {
                    "md_content": md_content,
                    "summary": summary,
                    "q_and_a": q_and_a,
                    "bullet_points": bullet_points,
                    "mind_map": mind_map,
                }
                
                st.success("Document processed successfully!")
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
```

### UI Component Flow

```mermaid
flowchart TD
    A[Page Load] --> B[Initialize Session State]
    B --> C[Setup Document Title]
    C --> D[Create File Upload Widget]
    D --> E{File Uploaded?}
    E -->|No| F[Show Upload Prompt]
    E -->|Yes| G[Show Process Button]
    G --> H[User Clicks Process]
    H --> I[Execute Workflow]
    I --> J[Store Results in Session]
    J --> K[Display Results]
    K --> L[Show Podcast Config]
    L --> M[User Configures Podcast]
    M --> N[Generate Audio]
    N --> O[Display Audio Player]
    
    subgraph "Session State Management"
        B1[workflow_results]
        B2[document_title]
    end
    
    subgraph "Results Display"
        K1[Summary]
        K2[Bullet Points]
        K3[FAQ Expander]
        K4[Mind Map]
    end
    
    B --> B1
    B --> B2
    K --> K1
    K --> K2
    K --> K3
    K --> K4
```

## Workflow Execution

### Synchronous Workflow Wrapper

The Streamlit app uses a sophisticated synchronous wrapper to handle async workflow execution:

```python
def sync_run_workflow(file: io.BytesIO, document_title: str):
    try:
        # Try to use existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, schedule the coroutine
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, run_workflow(file, document_title)
                )
                return future.result()
        else:
            return loop.run_until_complete(run_workflow(file, document_title))
    except RuntimeError:
        # No event loop exists, create one
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(run_workflow(file, document_title))
```

### Workflow Execution Flow

```mermaid
flowchart TD
    A[User Clicks Process] --> B[sync_run_workflow]
    B --> C{Event Loop Running?}
    C -->|Yes| D[ThreadPoolExecutor]
    C -->|No| E[run_until_complete]
    C -->|No Loop| F[asyncio.run]
    D --> G[run_workflow]
    E --> G
    F --> G
    G --> H[Create Temp File]
    H --> I[FileInputEvent]
    I --> J[WF.run]
    J --> K[extract_file_data Step]
    K --> L[Call process_file_tool]
    L --> M[MCP Server]
    M --> N[Return Extracted Data]
    N --> O[Parse Result]
    O --> P[MindMapCreationEvent]
    P --> Q[generate_mind_map Step]
    Q --> R[Call get_mind_map_tool]
    R --> S[MCP Server]
    S --> T[Return Mind Map]
    T --> U[NotebookOutputEvent]
    U --> V[Cleanup Temp File]
    V --> W[Return Results]
    W --> X[Update Session State]
    X --> Y[Display Results]
```

### Error Handling in Workflow

```mermaid
flowchart TD
    A[Workflow Execution] --> B{File Processing Success?}
    B -->|Yes| C[Continue to Mind Map]
    B -->|No| D[Return Error Message]
    C --> E{Mind Map Success?}
    E -->|Yes| F[Complete Workflow]
    E -->|No| G[Return Partial Results]
    
    subgraph "Error Recovery"
        H[File Processing Error]
        I[Network Error]
        J[API Error]
        K[Timeout Error]
    end
    
    subgraph "Error Responses"
        L[User-Friendly Messages]
        M[Logging for Debugging]
        N[Graceful Degradation]
    end
    
    D --> H
    D --> I
    D --> J
    D --> K
    H --> L
    I --> L
    J --> L
    K --> L
    L --> M
    M --> N
```

## Session State Management

### Session State Architecture

```mermaid
graph TB
    subgraph "Session State Variables"
        A[workflow_results]
        B[document_title]
    end
    
    subgraph "workflow_results Structure"
        C[md_content: str]
        D[summary: str]
        E[q_and_a: str]
        F[bullet_points: str]
        G[mind_map: str]
    end
    
    subgraph "State Management"
        H[Initialize on Page Load]
        I[Update on User Input]
        J[Persist Across Interactions]
        K[Clear on New Session]
    end
    
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    B --> H
    H --> I
    I --> J
    J --> K
```

### Session State Implementation

```python
# Initialize session state BEFORE creating the text input
if "workflow_results" not in st.session_state:
    st.session_state.workflow_results = None

if "document_title" not in st.session_state:
    st.session_state.document_title = randomname.get_name(
        adj=("music_theory", "geometry", "emotions"), 
        noun=("cats", "food")
    )

# Use session_state as the value and update it when changed
document_title = st.text_input(
    label="Document Title",
    value=st.session_state.document_title,
    key="document_title_input",
)

# Update session state when the input changes
if document_title != st.session_state.document_title:
    st.session_state.document_title = document_title
```

### State Persistence Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Session as Session State
    participant Workflow as Workflow Engine
    
    User->>UI: Enter document title
    UI->>Session: Update document_title
    Session-->>UI: Confirm update
    
    User->>UI: Upload file
    UI->>Session: Store file reference
    Session-->>UI: Confirm storage
    
    User->>UI: Click process
    UI->>Workflow: Execute workflow
    Workflow-->>UI: Return results
    UI->>Session: Store workflow_results
    Session-->>UI: Confirm storage
    
    User->>UI: Navigate away and back
    UI->>Session: Retrieve stored data
    Session-->>UI: Return workflow_results
    UI->>User: Display previous results
```

## File Processing Pipeline

### File Handling Process

```mermaid
flowchart TD
    A[File Upload] --> B[Streamlit File Handler]
    B --> C[io.BytesIO Object]
    C --> D[Create Temporary File]
    D --> E[Write File Content]
    E --> F[Flush to Disk]
    F --> G[Get File Path]
    G --> H[FileInputEvent]
    H --> I[Workflow Engine]
    I --> J[Process File Tool]
    J --> K[LlamaCloud Extract]
    K --> L[Return Results]
    L --> M[Cleanup Temp File]
    
    subgraph "Temporary File Management"
        N[temp.NamedTemporaryFile]
        O[delete=False]
        P[Manual cleanup]
    end
    
    subgraph "Error Handling"
        Q[File Write Error]
        R[File Read Error]
        S[Cleanup Error]
    end
    
    D --> N
    N --> O
    M --> P
    E --> Q
    G --> R
    M --> S
```

### File Processing Implementation

```python
async def run_workflow(file: io.BytesIO, document_title: str) -> Tuple[str, str, str, str, str]:
    # Create temp file with proper Windows handling
    with temp.NamedTemporaryFile(suffix=".pdf", delete=False) as fl:
        content = file.getvalue()
        fl.write(content)
        fl.flush()  # Ensure data is written
        temp_path = fl.name

    try:
        st_time = int(time.time() * 1000000)
        ev = FileInputEvent(file=temp_path)
        result: NotebookOutputEvent = await WF.run(start_event=ev)

        # Process results
        q_and_a = ""
        for q, a in zip(result.questions, result.answers):
            q_and_a += f"**{q}**\n\n{a}\n\n"
        bullet_points = "## Bullet Points\n\n- " + "\n- ".join(result.highlights)

        # Handle mind map
        mind_map = result.mind_map
        if Path(mind_map).is_file():
            mind_map = read_html_file(mind_map)
            try:
                os.remove(result.mind_map)
            except OSError:
                pass  # File might be locked on Windows

        end_time = int(time.time() * 1000000)
        sql_engine.to_sql_database(start_time=st_time, end_time=end_time)
        document_manager.put_documents([
            ManagedDocument(
                document_name=document_title,
                content=result.md_content,
                summary=result.summary,
                q_and_a=q_and_a,
                mindmap=mind_map,
                bullet_points=bullet_points,
            )
        ])
        return result.md_content, result.summary, q_and_a, bullet_points, mind_map

    finally:
        try:
            os.remove(temp_path)
        except OSError:
            await asyncio.sleep(0.1)
            try:
                os.remove(temp_path)
            except OSError:
                pass  # Give up if still locked
```

### Data Flow in File Processing

```mermaid
graph LR
    subgraph "Input Processing"
        A[PDF File] --> B[BytesIO Object]
        B --> C[Temporary File]
        C --> D[File Path]
    end
    
    subgraph "MCP Processing"
        D --> E[process_file_tool]
        E --> F[LlamaCloud Extract]
        F --> G[Structured Data]
        E --> H[LlamaParse]
        H --> I[Markdown Text]
    end
    
    subgraph "Result Processing"
        G --> J[Summary]
        G --> K[Questions & Answers]
        G --> L[Highlights]
        I --> M[Combined Result]
        J --> M
        K --> M
        L --> M
    end
    
    subgraph "Storage"
        M --> N[PostgreSQL]
        M --> O[Session State]
    end
```

## Audio Generation

### Podcast Configuration

The Streamlit app provides a comprehensive podcast configuration interface:

```python
# Podcast Configuration Panel
st.markdown("---")
st.markdown("## Podcast Configuration")

with st.expander("Customize Your Podcast", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        style = st.selectbox(
            "Conversation Style",
            ["conversational", "interview", "debate", "educational"],
            help="The overall style of the podcast conversation",
        )

        tone = st.selectbox(
            "Tone",
            ["friendly", "professional", "casual", "energetic"],
            help="The tone of voice for the conversation",
        )

        target_audience = st.selectbox(
            "Target Audience",
            ["general", "technical", "business", "expert", "beginner"],
            help="Who is the intended audience for this podcast?",
        )

    with col2:
        speaker1_role = st.text_input(
            "Speaker 1 Role",
            value="host",
            help="The role or persona of the first speaker",
        )

        speaker2_role = st.text_input(
            "Speaker 2 Role",
            value="guest",
            help="The role or persona of the second speaker",
        )

    # Focus Topics
    st.markdown("**Focus Topics** (optional)")
    focus_topics_input = st.text_area(
        "Enter topics to emphasize (one per line)",
        help="List specific topics you want the podcast to focus on. Leave empty for general coverage.",
        placeholder="How can this be applied for Machine Learning Applications?\nUnderstand the historical context\nFuture Implications",
    )

    # Parse focus topics
    focus_topics = None
    if focus_topics_input.strip():
        focus_topics = [
            topic.strip()
            for topic in focus_topics_input.split("\n")
            if topic.strip()
        ]

    # Custom Prompt
    custom_prompt = st.text_area(
        "Custom Instructions (optional)",
        help="Add any additional instructions for the podcast generation",
        placeholder="Make sure to explain technical concepts simply and include real-world examples...",
    )

    # Create config object
    podcast_config = PodcastConfig(
        style=style,
        tone=tone,
        focus_topics=focus_topics,
        target_audience=target_audience,
        custom_prompt=custom_prompt if custom_prompt.strip() else None,
        speaker1_role=speaker1_role,
        speaker2_role=speaker2_role,
    )
```

### Audio Generation Flow

```mermaid
flowchart TD
    A[User Configures Podcast] --> B[Create PodcastConfig]
    B --> C[User Clicks Generate]
    C --> D[sync_create_podcast]
    D --> E[Create Conversation]
    E --> F[OpenAI GPT-4]
    F --> G[Generate Script]
    G --> H[ElevenLabs API]
    H --> I[Generate Audio]
    I --> J[Return Audio File]
    J --> K[Display Audio Player]
    K --> L[Cleanup File]
    
    subgraph "Configuration Options"
        M[Conversation Style]
        N[Tone]
        O[Target Audience]
        P[Speaker Roles]
        Q[Focus Topics]
        R[Custom Instructions]
    end
    
    subgraph "Audio Processing"
        S[Text-to-Speech]
        T[Voice Synthesis]
        U[Audio Formatting]
    end
    
    B --> M
    B --> N
    B --> O
    B --> P
    B --> Q
    B --> R
    H --> S
    S --> T
    T --> U
```

### Audio Generation Implementation

```python
async def create_podcast(file_content: str, config: PodcastConfig = None):
    audio_fl = await PODCAST_GEN.create_conversation(
        file_transcript=file_content, 
        config=config
    )
    return audio_fl

def sync_create_podcast(file_content: str, config: PodcastConfig = None):
    return asyncio.run(create_podcast(file_content=file_content, config=config))

# Audio generation button
if st.button("Generate In-Depth Conversation", type="secondary"):
    with st.spinner("Generating podcast... This may take several minutes."):
        try:
            audio_file = sync_create_podcast(
                results["md_content"], 
                config=podcast_config
            )
            st.success("Podcast generated successfully!")

            # Display audio player
            st.markdown("## Generated Podcast")
            if os.path.exists(audio_file):
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                os.remove(audio_file)
                st.audio(audio_bytes, format="audio/mp3")
            else:
                st.error("Audio file not found.")

        except Exception as e:
            st.error(f"Error generating podcast: {str(e)}")
```

## Error Handling

### Comprehensive Error Handling Strategy

```mermaid
flowchart TD
    A[User Action] --> B{Validation Check}
    B -->|Pass| C[Execute Operation]
    B -->|Fail| D[Show Validation Error]
    C --> E{Operation Success?}
    E -->|Yes| F[Show Success Message]
    E -->|No| G[Handle Error]
    G --> H{Error Type}
    H -->|Network| I[Show Network Error]
    H -->|API| J[Show API Error]
    H -->|File| K[Show File Error]
    H -->|Unknown| L[Show Generic Error]
    
    subgraph "Error Recovery"
        M[Retry Operation]
        N[Fallback Mode]
        O[Graceful Degradation]
    end
    
    I --> M
    J --> M
    K --> N
    L --> O
```

### Error Handling Implementation

```python
# File processing error handling
if st.button("Process Document", type="primary"):
    with st.spinner("Processing document... This may take a few minutes."):
        try:
            md_content, summary, q_and_a, bullet_points, mind_map = (
                sync_run_workflow(file_input, st.session_state.document_title)
            )
            st.session_state.workflow_results = {
                "md_content": md_content,
                "summary": summary,
                "q_and_a": q_and_a,
                "bullet_points": bullet_points,
                "mind_map": mind_map,
            }
            st.success("Document processed successfully!")
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")

# Audio generation error handling
if st.button("Generate In-Depth Conversation", type="secondary"):
    with st.spinner("Generating podcast... This may take several minutes."):
        try:
            audio_file = sync_create_podcast(
                results["md_content"], 
                config=podcast_config
            )
            st.success("Podcast generated successfully!")

            # Display audio player
            st.markdown("## Generated Podcast")
            if os.path.exists(audio_file):
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                os.remove(audio_file)
                st.audio(audio_bytes, format="audio/mp3")
            else:
                st.error("Audio file not found.")

        except Exception as e:
            st.error(f"Error generating podcast: {str(e)}")
```

### Error Types and Handling

```mermaid
graph TB
    subgraph "Error Categories"
        A[Validation Errors]
        B[Network Errors]
        C[API Errors]
        D[File System Errors]
        E[Workflow Errors]
    end
    
    subgraph "Error Responses"
        F[User-Friendly Messages]
        G[Detailed Logging]
        H[Retry Mechanisms]
        I[Fallback Options]
    end
    
    subgraph "Error Recovery"
        J[Automatic Retry]
        K[Manual Retry Option]
        L[Alternative Paths]
        M[Graceful Degradation]
    end
    
    A --> F
    B --> G
    C --> H
    D --> I
    E --> J
    F --> K
    G --> L
    H --> M
```

## Configuration & Environment

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_OBSERVABILITY` | Enable/disable OpenTelemetry tracing | `true` | No |
| `OTLP_ENDPOINT` | OpenTelemetry collector endpoint | `http://localhost:4318/v1/traces` | No |
| `LLAMACLOUD_API_KEY` | LlamaCloud API key for extract and index | - | Yes |
| `EXTRACT_AGENT_ID` | LlamaCloud extract agent ID | - | Yes |
| `LLAMACLOUD_PIPELINE_ID` | LlamaCloud pipeline ID | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key for LLM operations | - | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for audio generation | - | No |
| `pgql_db` | PostgreSQL database name | `notebookllama` | Yes |
| `pgql_user` | PostgreSQL username | `llama` | Yes |
| `pgql_psw` | PostgreSQL password | `Salesforce1` | Yes |

### Configuration Loading

```python
# Environment configuration
load_dotenv()

# OpenTelemetry configuration
ENABLE_OBSERVABILITY = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"

if not ENABLE_OBSERVABILITY:
    # Disable OpenTelemetry at SDK level
    os.environ["OTEL_TRACES_SAMPLER"] = "off"
    os.environ["OTEL_TRACES_EXPORTER"] = "none"
    os.environ["OTEL_METRICS_EXPORTER"] = "none"
    os.environ["OTEL_LOGS_EXPORTER"] = "none"
    print("📊 OpenTelemetry disabled at SDK level")
else:
    print("📊 OpenTelemetry enabled")

# Database configuration
engine_url = f"postgresql+psycopg2://{os.getenv('pgql_user')}:{os.getenv('pgql_psw')}@localhost:5432/{os.getenv('pgql_db')}"
sql_engine = OtelTracesSqlEngine(
    engine_url=engine_url,
    table_name="agent_traces",
    service_name="agent.traces",
)
document_manager = DocumentManager(engine_url=engine_url)

# Workflow configuration
WF = NotebookLMWorkflow(timeout=600)
```

### Configuration Architecture

```mermaid
graph TB
    subgraph "Environment Loading"
        A[load_dotenv()]
        B[Load .env file]
        C[Set environment variables]
    end
    
    subgraph "Service Configuration"
        D[OpenTelemetry Config]
        E[Database Config]
        F[Workflow Config]
        G[API Keys]
    end
    
    subgraph "Runtime Configuration"
        H[Session State]
        I[UI Components]
        J[Error Handling]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I
    I --> J
```

## Development Guide

### Adding New UI Components

1. **Create Component Function**:
```python
def create_custom_component():
    st.markdown("## Custom Component")
    user_input = st.text_input("Enter data")
    if st.button("Process"):
        # Component logic
        pass
```

2. **Integrate with Session State**:
```python
if "custom_data" not in st.session_state:
    st.session_state.custom_data = None

# Update session state
st.session_state.custom_data = user_input
```

3. **Add Error Handling**:
```python
try:
    # Component logic
    st.success("Operation successful!")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

### Extending Workflow Integration

1. **Add New Workflow Step**:
```python
# In workflow.py
@step
async def custom_step(
    self,
    ev: PreviousEvent,
    mcp_client: Annotated[BasicMCPClient, Resource(get_mcp_client)]
) -> CustomEvent:
    result = await mcp_client.call_tool("custom_tool", {"data": ev.data})
    return CustomEvent(data=result)
```

2. **Update Frontend Integration**:
```python
# In Home.py
async def run_workflow(file: io.BytesIO, document_title: str):
    # ... existing code ...
    result: NotebookOutputEvent = await WF.run(start_event=ev)
    
    # Add custom processing
    custom_result = result.custom_data
    return result.md_content, result.summary, q_and_a, bullet_points, mind_map, custom_result
```

3. **Update UI Display**:
```python
# Display custom results
if st.session_state.workflow_results:
    results = st.session_state.workflow_results
    
    # Add custom section
    st.markdown("## Custom Results")
    st.markdown(results["custom_result"])
```

### Performance Optimization

#### 1. Caching

```python
@st.cache_data
def expensive_operation(data):
    # Expensive computation
    return result

@st.cache_resource
def load_model():
    # Load ML model once
    return model
```

#### 2. Async Operations

```python
async def async_operation():
    # Async operation
    pass

def sync_wrapper():
    return asyncio.run(async_operation())
```

#### 3. Session State Optimization

```python
# Use session state efficiently
if "computed_data" not in st.session_state:
    st.session_state.computed_data = expensive_computation()

# Access cached data
data = st.session_state.computed_data
```

### Testing

#### 1. Component Testing

```python
# Test individual components
def test_file_upload():
    # Mock file upload
    file_data = io.BytesIO(b"test content")
    result = process_file(file_data)
    assert result is not None
```

#### 2. Integration Testing

```python
# Test workflow integration
async def test_workflow():
    ev = FileInputEvent(file="test.pdf")
    result = await WF.run(start_event=ev)
    assert result.summary is not None
```

#### 3. UI Testing

```python
# Test UI components
def test_ui_components():
    # Test session state
    assert "workflow_results" in st.session_state
    # Test file upload
    # Test button interactions
```

### Debugging

#### 1. Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add logging to components
logger = logging.getLogger(__name__)
logger.debug("Processing file: %s", filename)
```

#### 2. Debug Mode

```python
# Enable debug mode
if st.checkbox("Debug Mode"):
    st.write("Session State:", st.session_state)
    st.write("Environment Variables:", dict(os.environ))
```

#### 3. Error Tracking

```python
# Track errors
try:
    # Operation
    pass
except Exception as e:
    st.error(f"Error: {str(e)}")
    # Log error for debugging
    logger.error("Operation failed", exc_info=True)
```

This comprehensive documentation provides a complete understanding of the Streamlit frontend architecture, its integration with the MCP server, and practical guidance for development and maintenance. 