from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.input_types import SourceBundleInput
from app.context_memory.ingest.input_assembler import InputAssembler


@dataclass(slots=True)
class IngestPipeline:
    input_assembler: InputAssembler

    def run(self) -> SourceBundleInput:
        return self.input_assembler.build_bundle()