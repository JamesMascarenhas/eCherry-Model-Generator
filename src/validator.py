from src.metamodel.metamodel import ReactorModel

_KNOWN_SPECIES = {"O2", "H2", "Hp", "OHm", "Kp", "H2O"}
_KNOWN_REACTIONS = {"OERdummy", "HERdummy"}
_VALID_SETUPS = {"continuous_0D_alkaline", "batch_0D_alkaline"}


def validate(model: ReactorModel) -> None:
    if len(model.electrolyte.c0) != len(model.electrolyte.species):
        raise ValueError(
            f"concentrations length ({len(model.electrolyte.c0)}) does not match "
            f"species length ({len(model.electrolyte.species)})"
        )

    if model.conditions.voltage >= 0:
        raise ValueError(
            f"voltage must be negative (got {model.conditions.voltage})"
        )

    if model.setup not in _VALID_SETUPS:
        raise ValueError(
            f"setup must be one of {sorted(_VALID_SETUPS)} (got '{model.setup}')"
        )

    if model.electrolyte.mode not in {"simple", "KOH"}:
        raise ValueError(
            f"electrolyte_mode must be 'simple' or 'KOH' (got '{model.electrolyte.mode}')"
        )

    unknown = [s for s in model.electrolyte.species if s not in _KNOWN_SPECIES]
    if unknown:
        raise ValueError(
            f"unrecognized species: {unknown}; known species are {sorted(_KNOWN_SPECIES)}"
        )

    for side, reaction in (("anode", model.anode.reaction), ("cathode", model.cathode.reaction)):
        if not reaction or reaction not in _KNOWN_REACTIONS:
            raise ValueError(
                f"{side} reaction must be one of {sorted(_KNOWN_REACTIONS)} (got '{reaction}')"
            )