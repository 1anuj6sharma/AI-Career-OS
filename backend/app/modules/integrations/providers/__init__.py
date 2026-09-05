from .base import OAuthProvider, PublicProfileProvider, ProviderError
from .github import GitHubProvider
from .linkedin import LinkedInProvider
from .leetcode import LeetCodeProvider
from .gfg import GeeksForGeeksProvider
from .kaggle import KaggleProvider
from .huggingface import HuggingFaceProvider
from .email_providers import GoogleProvider, MicrosoftProvider

def get_provider(provider_name: str):
    providers = {
        "github": GitHubProvider(),
        "linkedin": LinkedInProvider(),
        "leetcode": LeetCodeProvider(),
        "gfg": GeeksForGeeksProvider(),
        "kaggle": KaggleProvider(),
        "huggingface": HuggingFaceProvider(),
        "google": GoogleProvider(),
        "microsoft": MicrosoftProvider(),
    }
    provider = providers.get(provider_name.lower())
    if not provider:
        raise ValueError(f"Unsupported provider: {provider_name}")
    return provider

__all__ = ["OAuthProvider", "PublicProfileProvider", "ProviderError", "get_provider"]
