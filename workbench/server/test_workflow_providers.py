from workflow_engine import default_registry
from workflow_providers import probe_capabilities, register_real_providers


def test_real_providers_are_registered() -> None:
    registry = default_registry()
    register_real_providers(registry)
    names = {item['name'] for item in registry.describe()}
    assert {'python.callable', 'prolog.query', 'metta.evaluate', 'llm.complete', 'artifact.convert'} <= names


def test_capabilities_use_status_objects() -> None:
    registry = default_registry()
    register_real_providers(registry)
    capabilities = probe_capabilities(registry)
    assert capabilities
    assert all(value['status'] in {'implemented', 'partial', 'unavailable', 'failed'} for value in capabilities.values())
    assert capabilities['boundedLoops']['status'] == 'partial'
    assert capabilities['typedArtifacts']['status'] == 'partial'


def test_artifact_convert_provider_executes() -> None:
    registry = default_registry()
    register_real_providers(registry)
    provider = registry.get('artifact.convert')
    assert provider.handler({'value': {'x': 1}}, {'target': 'text'})['value'].strip().startswith('{')
