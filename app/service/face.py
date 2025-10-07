# app/services/face.py
import insightface
import os
import onnxruntime
import numpy as np
from typing import List

def _has_cuda() -> bool:
    # quick check: environment variable or onnxruntime available with GPU providers
    try:
        providers = onnxruntime.get_all_providers()
        # presence of 'CUDAExecutionProvider' suggests GPU runtime available
        return "CUDAExecutionProvider" in providers
    except Exception:
        return False

class FaceService:
    def __init__(self, model_name: str = "buffalo_l", det_size=(640,640)):
        self.model_name = model_name
        self.det_size = det_size
        self._init_model()

    def _init_model(self):
        use_gpu = _has_cuda()
        providers = ["CPUExecutionProvider"]
        if use_gpu:
            # if onnxruntime-gpu is present, this provider will enable CUDA
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

        self.app = insightface.app.FaceAnalysis(name=self.model_name, providers=providers)
        # ctx_id: -1 for CPU, 0 for GPU (insightface uses ctx id)
        ctx_id = 0 if use_gpu else -1
        self.app.prepare(ctx_id=ctx_id, det_size=self.det_size)

    def get(self, image: np.ndarray) -> List:
        """Return list of face objects from insightface app.get"""
        return self.app.get(image)
