from satorl.generators.base import Generator
from satorl.generators.gaussian import GaussianGenerator

_REGISTRY: dict[str, type[Generator]] = {
    GaussianGenerator.name: GaussianGenerator,
}

def get_generator(name: str) -> type[Generator]:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"Unknown generator {name!r}. Available: {', '.join(sorted(_REGISTRY))}"
        ) from None

def available_generators() -> list[str]:
    return sorted(_REGISTRY)