import tempfile as temp
import os
import uuid
from dotenv import load_dotenv

from pydub import AudioSegment
from elevenlabs import AsyncElevenLabs
from llama_index.core.llms.structured_llm import StructuredLLM
from typing_extensions import Self
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, model_validator, Field
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAIResponses


class ConversationTurn(BaseModel):
    speaker: Literal["speaker1", "speaker2"] = Field(
        description="The person who is speaking",
    )
    content: str = Field(
        description="The content of the speech",
    )


class MultiTurnConversation(BaseModel):
    conversation: List[ConversationTurn] = Field(
        description="List of conversation turns. Conversation must start with speaker1, and continue with an alternance of speaker1 and speaker2",
        min_length=3,
        max_length=50,
        examples=[
            [
                ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
                ConversationTurn(
                    speaker="speaker2", content="I am very well, how about you?"
                ),
                ConversationTurn(speaker="speaker1", content="I am well too, thanks!"),
            ]
        ],
    )

    @model_validator(mode="after")
    def validate_conversation(self) -> Self:
        speakers = [turn.speaker for turn in self.conversation]
        if speakers[0] != "speaker1":
            raise ValueError("Conversation must start with speaker1")
        for i, speaker in enumerate(speakers):
            if i % 2 == 0 and speaker != "speaker1":
                raise ValueError(
                    "Conversation must be an alternance between speaker1 and speaker2"
                )
            elif i % 2 != 0 and speaker != "speaker2":
                raise ValueError(
                    "Conversation must be an alternance between speaker1 and speaker2"
                )
            continue
        return self


class PodcastConfig(BaseModel):
    """Configuration for podcast generation"""

    # Basic style options
    style: Literal["conversational", "interview", "debate", "educational"] = Field(
        default="conversational",
        description="The style of the conversation",
    )
    tone: Literal["friendly", "professional", "casual", "energetic"] = Field(
        default="friendly",
        description="The tone of the conversation",
    )

    # Content focus
    focus_topics: Optional[List[str]] = Field(
        default=None, description="Specific topics to focus on during the conversation"
    )

    # Audience targeting
    target_audience: Literal[
        "general", "technical", "business", "expert", "beginner"
    ] = Field(
        default="general",
        description="The target audience for the conversation",
    )

    # Custom user prompt
    custom_prompt: Optional[str] = Field(
        default=None, description="Additional instructions for the conversation"
    )

    # Speaker customization
    speaker1_role: str = Field(
        default="host", description="The role of the first speaker"
    )
    speaker2_role: str = Field(
        default="guest", description="The role of the second speaker"
    )


class PodcastGenerator(BaseModel):
    llm: StructuredLLM
    client: AsyncElevenLabs

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_podcast(self) -> Self:
        try:
            assert self.llm.output_cls == MultiTurnConversation
        except AssertionError:
            raise ValueError(
                f"The output class of the structured LLM must be {MultiTurnConversation.__qualname__}, your LLM has output class: {self.llm.output_cls.__qualname__}"
            )
        return self

    def _build_conversation_prompt(
        self, file_transcript: str, config: PodcastConfig
    ) -> str:
        """Build a customized prompt based on the configuration"""

        # Base prompt with style and tone
        prompt = f"""Create a {config.style} podcast conversation with two speakers from this transcript.

        CONVERSATION STYLE: {config.style}
        TONE: {config.tone}
        TARGET AUDIENCE: {config.target_audience}

        SPEAKER ROLES:
        - Speaker 1: {config.speaker1_role}
        - Speaker 2: {config.speaker2_role}
        """

        if config.focus_topics:
            prompt += "\nFOCUS TOPICS: Make sure to discuss these topics in detail:\n"
            for topic in config.focus_topics:
                prompt += f"- {topic}\n"

        # Add audience-specific instructions
        audience_instructions = {
            "technical": "Use technical terminology appropriately and dive deep into technical details.",
            "beginner": "Explain concepts clearly and avoid jargon. Define technical terms when used.",
            "expert": "Assume advanced knowledge and discuss nuanced aspects and implications.",
            "business": "Focus on practical applications, ROI, and strategic implications.",
            "general": "Balance accessibility with depth, explaining key concepts clearly.",
        }

        prompt += (
            f"\nAUDIENCE APPROACH: {audience_instructions[config.target_audience]}\n"
        )

        # Add custom prompt if provided
        if config.custom_prompt:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {config.custom_prompt}\n"

        # Add the source material
        prompt += f"\nSOURCE MATERIAL:\n'''\n{file_transcript}\n'''\n"

        # Add final instructions
        prompt += """
        IMPORTANT: Create an engaging, natural conversation that flows well between the two speakers.
        The conversation should feel authentic and provide value to the target audience.
        """

        return prompt

    async def _conversation_script(
        self, file_transcript: str, config: PodcastConfig
    ) -> MultiTurnConversation:
        """Generate conversation script with customization"""
        prompt = self._build_conversation_prompt(file_transcript, config)

        response = await self.llm.achat(
            messages=[
                ChatMessage(
                    role="user",
                    content=prompt,
                )
            ]
        )
        return MultiTurnConversation.model_validate_json(response.message.content)

    async def _conversation_audio(self, conversation: MultiTurnConversation) -> str:
        """Generate audio for the conversation"""
        files: List[str] = []
        for turn in conversation.conversation:
            if turn.speaker == "speaker1":
                speech_iterator = self.client.text_to_speech.convert(
                    voice_id="nPczCjzI2devNBz1zQrb",
                    text=turn.content,
                    output_format="mp3_22050_32",
                    model_id="eleven_turbo_v2_5",
                )
            else:
                speech_iterator = self.client.text_to_speech.convert(
                    voice_id="Xb7hH8MSUJpSbSDYk0k2",
                    text=turn.content,
                    output_format="mp3_22050_32",
                    model_id="eleven_turbo_v2_5",
                )
            fl = temp.NamedTemporaryFile(
                suffix=".mp3", delete=False, delete_on_close=False
            )
            with open(fl.name, "wb") as f:
                async for chunk in speech_iterator:
                    if chunk:
                        f.write(chunk)
            files.append(fl.name)

        output_path = f"conversation_{str(uuid.uuid4())}.mp3"
        combined_audio: AudioSegment = AudioSegment.empty()

        for file_path in files:
            audio = AudioSegment.from_file(file_path)
            combined_audio += audio

            # Export with high quality MP3 settings
            combined_audio.export(
                output_path,
                format="mp3",
                bitrate="320k",  # High quality bitrate
                parameters=["-q:a", "0"],  # Highest quality
            )
            os.remove(file_path)

        return output_path

    async def create_conversation(
        self, file_transcript: str, config: Optional[PodcastConfig] = None
    ):
        """Main method to create a customized podcast conversation"""
        if config is None:
            config = PodcastConfig()

        conversation = await self._conversation_script(
            file_transcript=file_transcript, config=config
        )
        podcast_file = await self._conversation_audio(conversation=conversation)
        return podcast_file


load_dotenv()

if os.getenv("ELEVENLABS_API_KEY", None) and os.getenv("OPENAI_API_KEY", None):
    SLLM = OpenAIResponses(
        model="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY")
    ).as_structured_llm(MultiTurnConversation)
    EL_CLIENT = AsyncElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    PODCAST_GEN = PodcastGenerator(llm=SLLM, client=EL_CLIENT)
