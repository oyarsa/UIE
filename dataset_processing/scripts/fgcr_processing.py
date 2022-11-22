"""Script to convert FGCR data into the relation format.

1. Create the data/fgcr folder in this repository
2. Clone the FGCR repository (https://github.com/YangLinyi/Fine-grained-Causal-Reasoning)
   somewhere else
3. Move the files from the `event` folder in FGCR to data/fgcr
```
$ tree data/fgcr
data/fgcr
├── event_dataset_dev.json
├── event_dataset_test.json
└── event_dataset_train.json
```
4. Run `bash run_fgcr_data_generation.bash`
"""
from __future__ import annotations
from dataclasses import dataclass

import json
from pathlib import Path
import sys
from typing import Any, Iterable

from nltk.tokenize import word_tokenize


def tokenise(sentence: str) -> list[str]:
    return word_tokenize(sentence)


class Entities:
    def __init__(self) -> None:
        # map from entity (a tuple of start,end) to its index
        self.entities: dict[tuple[int, int], tuple[int, str]] = {}
        self.idx_counter = 0

    def add_entities(self, entities: list[list[int]], kind: str) -> None:
        if not entities:
            return
        for entity in entities:
            start, end = tuple(entity)
            if (start, end) not in self.entities:
                self.entities[(start, end)] = (self.idx_counter, kind)
                self.idx_counter += 1

    def get_entity_index(self, entity: Iterable[int]) -> int:
        idx, _ = self.entities[tuple(entity)]
        return idx


@dataclass
class Relation:
    kind: str
    cause_idx: int
    effect_idx: int


def convert_instance(instance: dict[str, Any]) -> dict[str, Any]:
    entities = Entities()
    for relation in instance["labelData"]:
        if len(relation["result"]) > 1 and len(relation["reason"]) > 1:
            continue
        entities.add_entities(relation["reason"], "cause")
        entities.add_entities(relation["result"], "effect")

    relations = []
    for relation in instance["labelData"]:
        causes = relation["reason"]
        effects = relation["result"]

        if len(causes) > 1 and len(effects) > 1:
            print("Relation with N to M cause/effects. Skipping.", causes, effects)
            continue
        if not causes or not effects:
            print("Relation without cause or effect. Skipping.", causes, effects)
            continue

        if len(causes) > 1:
            assert len(effects) == 1
            effect = entities.get_entity_index(effects[0])
            for cause in causes:
                relations.append(
                    Relation(relation["type"], entities.get_entity_index(cause), effect)
                )
        elif len(effects) > 1:
            assert len(causes) == 1
            cause = entities.get_entity_index(causes[0])
            for effect in effects:
                relations.append(
                    Relation(relation["type"], cause, entities.get_entity_index(effect))
                )
        else:
            assert len(causes) == len(effects) and len(causes) == 1
            relations.append(
                Relation(
                    relation["type"],
                    entities.get_entity_index(causes[0]),
                    entities.get_entity_index(effects[0]),
                )
            )

    span_pair_list = []
    for relation in relations:
        span_pair_list.append(
            {
                "type": relation.kind,
                "head": relation.cause_idx,
                "tail": relation.effect_idx,
            }
        )

    span_list = []
    for (start, end), (_, kind) in entities.entities.items():
        span_list.append(
            {
                "type": kind,
                "start": start,
                "end": end,
            }
        )

    converted = {
        "id": str(instance["tid"]),
        "tokens": tokenise(instance["info"]),
        "span_pair_list": span_pair_list,
        "span_list": span_list,
    }
    return converted


def convert_file(infile: Path, outfile: Path) -> None:
    with open(infile) as f:
        dataset = json.load(f)

    converted = [convert_instance(instance) for instance in dataset]
    with open(outfile, "w") as f:
        for c in converted:
            print(json.dumps(c), file=f)


def main() -> None:
    raw_folder = Path("data/fgcr")
    new_folder = Path("data/relation/fgcr")

    splits = ["dev", "test", "train"]
    for split in splits:
        raw_path = raw_folder / f"event_dataset_{split}.json"
        new_path = new_folder / f"{split}.jsonlines"
        convert_file(raw_path, new_path)


if __name__ == "__main__":
    main()
