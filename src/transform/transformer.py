from src.metamodel.metamodel import ReactorModel
from src.validator import validate

_LIB   = "eCherry_Library"
_ALIAS = "Echery_library"  # spelling used in eCherry examples

_SPECIES_FQN: dict[str, str] = {
    "O2":  f"{_LIB}.Data.DataRecords.Species.GaseousSpecies.O2",
    "H2":  f"{_LIB}.Data.DataRecords.Species.GaseousSpecies.H2",
    "Hp":  f"{_LIB}.Data.DataRecords.Species.DissolvedSpecies.Hp",
    "OHm": f"{_LIB}.Data.DataRecords.Species.DissolvedSpecies.OHm",
    "Kp":  f"{_LIB}.Data.DataRecords.Species.DissolvedSpecies.Kp",
    "H2O": f"{_LIB}.Data.DataRecords.Species.LiquidSpecies.H2O",
}

_REACTION_FQN: dict[str, str] = {
    "OERdummy": f"{_LIB}.Data.DataRecords.ElecReaction.List_Of_Reactions.OERdummy",
    "HERdummy": f"{_LIB}.Data.DataRecords.ElecReaction.List_Of_Reactions.HERdummy",
}

_USER_INPUT_RECORD: dict[str, str] = {
    "simple": "Example_AlkalineWaterElectrolysis",
    "KOH":    "Example_AlkalineWaterElectrolysis_KOH",
}


def transform(model: ReactorModel) -> dict:
    validate(model)

    mode         = model.electrolyte.mode
    c0           = model.electrolyte.c0
    inflow_scale = model.conditions.inflow_scale
    is_batch     = model.setup == "batch_0D_alkaline"

    return {
        # --- identity ---
        "name":                   model.name,
        "electrolyte_mode":       mode,
        "user_input_record_name": model.name + "_UserInput",
        "baseline_record_name":   _USER_INPUT_RECORD[mode],

        # --- Modelica package placement ---
        "within_user_input": f"{_LIB}.Data.UserInput",
        "within_model": (
            f"{_LIB}.Examples.Batch.Batch0D"
            if is_batch else
            f"{_LIB}.Examples.Continuous"
        ),

        # --- import alias (used in generated model body) ---
        "import_alias":  _ALIAS,
        "import_target": _LIB,

        # --- component FQNs (via import alias) ---
        "fqn_voltage_source":   f"{_ALIAS}.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed",
        "fqn_electrode":        f"{_ALIAS}.ElectrochemicalReactor.Electrodes.Electrode_Planar",
        "fqn_electrolyte": (
            f"{_ALIAS}.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_0D_L"
            if is_batch else
            f"{_ALIAS}.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L"
        ),
        "fqn_separator":        f"{_ALIAS}.ElectrochemicalReactor.Separators.Diaphragm_Hydroxide",
        "fqn_inflow":           f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed",
        "fqn_connecting_flow":  f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow",
        "fqn_environment":      f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain.Flows.Environment",
        "fqn_ground":           "Modelica.Electrical.Analog.Basic.Ground",

        # --- batch flag ---
        "is_batch": is_batch,

        # --- KOH-only conductivity redeclare ---
        "use_koh_conductivity": mode == "KOH",
        "fqn_koh_conductivity": (
            f"{_LIB}.ElectrochemicalReactor.Properties.ConductivityModels"
            ".ConductivityElectrolyteCalcKOH"
        ),

        # --- data record FQNs (full, used in UserInput record) ---
        "fqn_species_record":  f"{_LIB}.Data.DataRecords.Species.SpeciesRecord",
        "fqn_reaction_record": f"{_LIB}.Data.DataRecords.ElecReaction.Reaction",
        "fqn_geometry":        f"{_LIB}.Data.DataRecords.Geometry",
        "fqn_conditions":      f"{_LIB}.Data.DataRecords.Conditions",

        # --- species ---
        "species":      model.electrolyte.species,
        "species_fqns": [_SPECIES_FQN[s] for s in model.electrolyte.species],

        # --- reactions ---
        "anode_reaction":       model.anode.reaction,
        "cathode_reaction":     model.cathode.reaction,
        "anode_reaction_fqn":   _REACTION_FQN[model.anode.reaction],
        "cathode_reaction_fqn": _REACTION_FQN[model.cathode.reaction],

        # --- electrical ---
        "voltage": model.conditions.voltage,

        # --- geometry (flat) ---
        "geo_X":          model.geometry.X,
        "geo_X_membrane": model.geometry.X_membrane,
        "geo_Y":          model.geometry.Y,
        "geo_Z":          model.geometry.Z,
        "geo_cond0":      model.geometry.cond0,
        "geo_dX":         model.geometry.dX,

        # --- operating conditions (flat) ---
        "T0":           model.conditions.T0,
        "Tenvironment": model.conditions.Tenvironment,
        "p":            model.conditions.p,

        # --- concentrations ---
        "c0":             c0,
        "pi":             [100000] * len(model.electrolyte.species),
        "inflow_molflow": [c * inflow_scale for c in c0],

        # --- conductivity ---
        "kappa_anode":   model.anode.kappa,
        "kappa_cathode": model.cathode.kappa,

        # --- separator ---
        "diaphragm_kappa": model.separator.kappa,
        "diaphragm_X":     model.geometry.X_membrane,

        # --- flow scaling ---
        "inflow_scale": inflow_scale,

        # --- simulation ---
        "sim_stop_time": model.sim_stop_time,
    }