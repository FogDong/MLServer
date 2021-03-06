import pytest
import os

from mlserver.models.sklearn import (
    _SKLEARN_PRESENT,
    SKLearnModel,
    PREDICT_OUTPUT,
    PREDICT_PROBA_OUTPUT,
    WELLKNOWN_MODEL_FILENAMES,
)
from mlserver.settings import ModelSettings
from mlserver.errors import InferenceError
from mlserver.types import RequestOutput

from .helpers import skipif_sklearn_missing

if _SKLEARN_PRESENT:
    from sklearn.dummy import DummyClassifier


@skipif_sklearn_missing
def test_sklearn_load(sklearn_model: SKLearnModel):
    assert sklearn_model.ready
    assert type(sklearn_model._model) == DummyClassifier


@skipif_sklearn_missing
@pytest.mark.parametrize("fname", WELLKNOWN_MODEL_FILENAMES)
async def test_sklearn_load_folder(
    fname, sklearn_model_uri: str, sklearn_model_settings: ModelSettings
):
    model_uri = os.path.dirname(sklearn_model_uri)
    model_path = os.path.join(model_uri, fname)
    os.rename(sklearn_model_uri, model_path)

    sklearn_model_settings.parameters.uri = model_uri  # type: ignore

    model = SKLearnModel(sklearn_model_settings)
    await model.load()

    assert model.ready
    assert type(model._model) == DummyClassifier


@skipif_sklearn_missing
async def test_sklearn_multiple_inputs_error(
    sklearn_model: SKLearnModel, inference_request
):
    with pytest.raises(InferenceError):
        await sklearn_model.predict(inference_request)


@skipif_sklearn_missing
async def test_sklearn_invalid_output_error(
    sklearn_model: SKLearnModel, sklearn_inference_request
):
    sklearn_inference_request.outputs = [RequestOutput(name="something_else")]

    with pytest.raises(InferenceError):
        await sklearn_model.predict(sklearn_inference_request)


@skipif_sklearn_missing
@pytest.mark.parametrize(
    "req_outputs",
    [
        [],
        [PREDICT_OUTPUT],
        [PREDICT_PROBA_OUTPUT],
        [PREDICT_OUTPUT, PREDICT_PROBA_OUTPUT],
    ],
)
async def test_sklearn_predict(
    sklearn_model: SKLearnModel, sklearn_inference_request, req_outputs
):
    sklearn_inference_request.outputs = [
        RequestOutput(name=req_output) for req_output in req_outputs
    ]

    response = await sklearn_model.predict(sklearn_inference_request)

    input_data = sklearn_inference_request.inputs[0].data
    if len(req_outputs) == 0:
        # Assert that PREDICT_OUTPUT is added by default
        req_outputs = [PREDICT_OUTPUT]

    assert len(response.outputs) == len(req_outputs)
    for req_output, output in zip(req_outputs, response.outputs):
        assert output.name == req_output
        assert len(output.data) == len(input_data)  # type: ignore
