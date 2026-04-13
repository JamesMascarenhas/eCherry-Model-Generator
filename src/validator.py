from src.metamodel.metamodel import ReactorModel

_KNOWN_SPECIES   = {"O2", "H2", "Hp", "OHm", "Kp", "H2O", "N2", "NH3"}
_KNOWN_REACTIONS = {"OERdummy", "HERdummy", "NRRdummy"}
_VALID_SETUPS    = {"continuous_0D_alkaline", "batch_0D_alkaline", "continuous_0D_ammonia"}


def validate(model: ReactorModel) -> None:
    n_species = len(model.electrolyte.species)

    # 1. Electrolyte concentration array length
    if len(model.electrolyte.c0) != n_species:
        raise ValueError(
            f"concentrations length ({len(model.electrolyte.c0)}) does not match "
            f"species length ({n_species})"
        )

    # 2. Voltage must be negative
    if model.conditions.voltage >= 0:
        raise ValueError(
            f"voltage must be negative (got {model.conditions.voltage})"
        )

    # 3. Valid setup
    if model.setup not in _VALID_SETUPS:
        raise ValueError(
            f"setup must be one of {sorted(_VALID_SETUPS)} (got '{model.setup}')"
        )

    # 4. Valid electrolyte mode — only enforced for non-ammonia families
    if model.setup != "continuous_0D_ammonia":
        if model.electrolyte.mode not in {"simple", "KOH"}:
            raise ValueError(
                f"electrolyte_mode must be 'simple' or 'KOH' (got '{model.electrolyte.mode}')"
            )

    # 5. All species recognized
    unknown = [s for s in model.electrolyte.species if s not in _KNOWN_SPECIES]
    if unknown:
        raise ValueError(
            f"unrecognized species: {unknown}; known species are {sorted(_KNOWN_SPECIES)}"
        )

    # 6. Primary reactions recognized
    for side, reaction in (("anode", model.anode.reaction), ("cathode", model.cathode.reaction)):
        if not reaction or reaction not in _KNOWN_REACTIONS:
            raise ValueError(
                f"{side} reaction must be one of {sorted(_KNOWN_REACTIONS)} (got '{reaction}')"
            )

    # 7. Extra cathode reactions recognized
    for rxn in (model.cathode.extra_reactions or []):
        if rxn not in _KNOWN_REACTIONS:
            raise ValueError(
                f"extra cathode reaction must be one of {sorted(_KNOWN_REACTIONS)} (got '{rxn}')"
            )

    # 8. Ammonia-specific checks (grouped)
    if model.setup == "continuous_0D_ammonia":
        if model.gas_channel_params is None:
            raise ValueError(
                "setup 'continuous_0D_ammonia' requires a gas_channel { ... } block in the DSL"
            )
        if len(model.gas_channel_params.c0_gas_channel) != n_species:
            raise ValueError(
                f"gas_channel concentrations length ({len(model.gas_channel_params.c0_gas_channel)}) "
                f"does not match species length ({n_species})"
            )
        if len(model.gas_channel_params.mol_vec_frac0) != n_species:
            raise ValueError(
                f"mol_vec_frac0 length ({len(model.gas_channel_params.mol_vec_frac0)}) "
                f"does not match species length ({n_species})"
            )
        if model.cathode.kind != "gas_diffusion":
            raise ValueError(
                "setup 'continuous_0D_ammonia' requires cathode_type: gas_diffusion in the reactions block"
            )