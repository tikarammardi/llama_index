from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.embeddings.huggingface_openvino import OpenVINOEmbedding


def test_openvinoembedding_class():
    names_of_base_classes = [b.__name__ for b in OpenVINOEmbedding.__mro__]
    assert BaseEmbedding.__name__ in names_of_base_classes


def test_openvinoembedding_get_text_embedding(tmp_path):
    model_dir = str(tmp_path / "models/bge_ov")
    OpenVINOEmbedding.create_and_save_openvino_model(
        "BAAI/bge-small-en-v1.5", model_dir
    )
    embed_model = OpenVINOEmbedding(folder_name=model_dir)
    embeddings = embed_model.get_text_embedding("Hello World!")

    assert len(embeddings) == 384
    gold_embeddings = [
        -0.0032756966538727283,
        -0.011690770275890827,
        0.04155917093157768,
        -0.038148097693920135,
        0.024183034896850586,
    ]

    for i in range(5):
        assert abs(embeddings[i] - gold_embeddings[i]) < 1e-4