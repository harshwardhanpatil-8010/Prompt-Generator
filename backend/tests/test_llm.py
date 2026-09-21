from backend.llm import get_llm_provider
from backend.llm.mock import MockLLMProvider
from backend.llm.ollama import OllamaLLMProvider


def test_mock_llm_domain_awareness():
    mock = MockLLMProvider()
    gym_intent = mock.extract_intent("Create a local gym website with trainers")
    assert gym_intent.business_domain == "Fitness & Health"

    sneaker_intent = mock.extract_intent("Build an ecommerce online sneaker store with cart")
    assert sneaker_intent.business_domain == "Sneaker & Footwear Retail"


def test_ollama_fallback_on_unreachable():
    ollama = OllamaLLMProvider(base_url="http://127.0.0.1:99999", model="non-existent")
    intent = ollama.extract_intent("Create a portfolio website for a developer")
    assert intent is not None
    assert intent.business_domain == "Personal Portfolio"


def test_get_llm_provider_factory():
    provider_mock = get_llm_provider("mock")
    assert isinstance(provider_mock, MockLLMProvider)

    provider_ollama = get_llm_provider("ollama")
    assert isinstance(provider_ollama, OllamaLLMProvider)
