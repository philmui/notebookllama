import pytest

from src.notebookllama.models import (
    Notebook,
)
from src.notebookllama.verifying import ClaimVerification
from src.notebookllama.mindmap import MindMap, Node, Edge
from src.notebookllama.audio import MultiTurnConversation, ConversationTurn
from src.notebookllama.documents import ManagedDocument
from pydantic import ValidationError


def test_notebook() -> None:
    n1 = Notebook(
        summary="This is a summary",
        questions=[
            "What is the capital of Spain?",
            "What is the capital of France?",
            "What is the capital of Italy?",
            "What is the capital of Portugal?",
            "What is the capital of Germany?",
        ],
        answers=[
            "Madrid",
            "Paris",
            "Rome",
            "Lisbon",
            "Berlin",
        ],
        highlights=["This", "is", "a", "summary"],
    )
    assert n1.summary == "This is a summary"
    assert n1.questions[0] == "What is the capital of Spain?"
    assert n1.answers[0] == "Madrid"
    assert n1.highlights[0] == "This"
    # Fewer answers than questions
    with pytest.raises(ValidationError):
        Notebook(
            summary="This is a summary",
            questions=[
                "What is the capital of France?",
                "What is the capital of Italy?",
                "What is the capital of Portugal?",
                "What is the capital of Germany?",
            ],
            answers=[
                "Paris",
                "Rome",
                "Lisbon",
            ],
            highlights=["This", "is", "a", "summary"],
        )
    # Fewer highlights than required
    with pytest.raises(ValidationError):
        Notebook(
            summary="This is a summary",
            questions=[
                "What is the capital of Spain?",
                "What is the capital of France?",
                "What is the capital of Italy?",
                "What is the capital of Portugal?",
                "What is the capital of Germany?",
            ],
            answers=[
                "Madrid",
                "Paris",
                "Rome",
                "Lisbon",
                "Berlin",
            ],
            highlights=["This", "is"],
        )


def test_mind_map() -> None:
    m1 = MindMap(
        nodes=[
            Node(id="A", content="Auxin is released"),
            Node(id="B", content="Travels to the roots"),
            Node(id="C", content="Root cells grow"),
        ],
        edges=[
            Edge(from_id="A", to_id="B"),
            Edge(from_id="A", to_id="C"),
            Edge(from_id="B", to_id="C"),
        ],
    )
    assert m1.nodes[0].id == "A"
    assert m1.nodes[0].content == "Auxin is released"
    assert m1.edges[0].from_id == "A"
    assert m1.edges[0].to_id == "B"

    with pytest.raises(ValidationError):
        MindMap(
            nodes=[
                Node(id="A", content="Auxin is released"),
                Node(id="B", content="Travels to the roots"),
                Node(id="C", content="Root cells grow"),
            ],
            edges=[
                Edge(from_id="A", to_id="B"),
                Edge(from_id="A", to_id="D"),  # "D" does not exist
                Edge(from_id="B", to_id="C"),
            ],
        )


def test_multi_turn_conversation() -> None:
    turns = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker2", content="I am very well, how about you?"),
        ConversationTurn(speaker="speaker1", content="I am well too, thanks!"),
    ]
    assert turns[0].speaker == "speaker1"
    assert turns[0].content == "Hello, who are you?"
    conversation = MultiTurnConversation(
        conversation=turns,
    )
    assert isinstance(conversation.conversation, list)
    assert isinstance(conversation.conversation[0], ConversationTurn)
    wrong_turns = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker2", content="I am very well, how about you?"),
    ]
    wrong_turns1 = [
        ConversationTurn(speaker="speaker2", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker1", content="I am very well, how about you?"),
        ConversationTurn(speaker="speaker2", content="I am well too!"),
    ]
    wrong_turns2 = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker1", content="How is your life going?"),
        ConversationTurn(
            speaker="speaker2",
            content="What is all this interest in me all of a sudden?!",
        ),
    ]
    wrong_turns3 = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker2", content="I'm well! But..."),
        ConversationTurn(
            speaker="speaker2",
            content="...What is all this interest in me all of a sudden?!",
        ),
    ]
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns)
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns1)
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns2)
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns3)


def test_claim_verification() -> None:
    cl1 = ClaimVerification(
        claim_is_true=True, supporting_citations=["Support 1", "Support 2"]
    )
    assert cl1.claim_is_true
    assert cl1.supporting_citations == ["Support 1", "Support 2"]
    cl2 = ClaimVerification(
        claim_is_true=False, supporting_citations=["Support 1", "Support 2"]
    )
    assert cl2.supporting_citations == ["The claim was deemed false."]
    cl3 = ClaimVerification(
        claim_is_true=False,
    )
    assert cl3.supporting_citations is None
    with pytest.raises(ValidationError):
        ClaimVerification(
            claim_is_true=True,
            supporting_citations=["Support 1", "Support 2", "Support 3", "Support 4"],
        )


def test_managed_documents() -> None:
    d1 = ManagedDocument(
        document_name="Hello World",
        content="This is a test",
        summary="Test",
        q_and_a="Hello? World.",
        mindmap="Hello -> World",
        bullet_points=". Hello, . World",
    )
    assert d1.document_name == "Hello World"
    assert d1.content == "This is a test"
    assert d1.summary == "Test"
    assert d1.q_and_a == "Hello? World."
    assert d1.mindmap == "Hello -> World"
    assert d1.bullet_points == ". Hello, . World"
    d2 = ManagedDocument(
        document_name="Hello World",
        content="This is a test",
        summary="Test's child",
        q_and_a="Hello? World.",
        mindmap="Hello -> World",
        bullet_points=". Hello, . World",
    )
    assert d2.summary == "Test's child"
