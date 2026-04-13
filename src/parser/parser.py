from src.metamodel.metamodel import (
    ReactorModel,
    GeometryParams,
    OperatingConditions,
    Electrode,
    Separator,
    Electrolyte,
    FlowChannel,
    GasChannelParams,
)

_REACTION_MAP = {
    "OER":      "OERdummy",
    "OERdummy": "OERdummy",
    "HER":      "HERdummy",
    "HERdummy": "HERdummy",
    "NRR":      "NRRdummy",   # ammonia
    "NRRdummy": "NRRdummy",   # ammonia
}


def _parse_value(s: str):
    """Parse a scalar or bracketed list value from a stripped string."""
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        items = [item.strip() for item in s[1:-1].split(",") if item.strip()]
        parsed = []
        for item in items:
            try:
                parsed.append(float(item))
            except ValueError:
                parsed.append(item)
        return parsed
    try:
        return float(s)
    except ValueError:
        return s


def _parse_to_dict(filepath: str) -> dict:
    """Read a .reactor file and return a flat intermediate dict."""
    with open(filepath) as f:
        lines = [line.split("//")[0].strip() for line in f]
    lines = [l for l in lines if l]

    # locate the reactor header line
    i = 0
    while i < len(lines) and not (lines[i].startswith("reactor ") and "{" in lines[i]):
        i += 1

    name = lines[i].split()[1]
    i += 1  # advance past the opening {

    data: dict = {"name": name}

    while i < len(lines):
        line = lines[i]

        if line == "}":
            break

        if line.endswith("{"):
            # sub-block: collect key-value pairs until the matching }
            block_name = line[:-1].strip()
            i += 1
            block: dict = {}
            while i < len(lines) and lines[i] != "}":
                sub = lines[i]
                if ":" in sub:
                    k, _, v = sub.partition(":")
                    block[k.strip()] = _parse_value(v)
                i += 1
            i += 1  # skip closing }
            data[block_name] = block

        elif ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = _parse_value(v)
            i += 1

        else:
            i += 1

    return data


def _resolve_reaction(raw) -> str:
    """Map a single reaction name (str or float-parsed) to its canonical form."""
    return _REACTION_MAP.get(str(raw).strip(), str(raw).strip())


def _build_model(data: dict) -> ReactorModel:
    """Construct a ReactorModel from the intermediate dict."""
    geo  = data.get("geometry", {})
    cond = data.get("conditions", {})
    elec = data.get("electrolyte", {})
    diap = data.get("diaphragm", {})
    reac = data.get("reactions", {})
    sim  = data.get("simulation", {})

    geometry = GeometryParams(
        X=float(geo.get("X", 0.01)),
        X_membrane=float(geo.get("X_membrane", 0.0005)),
        Y=float(geo.get("Y", 1.0)),
        Z=float(geo.get("Z", 1.0)),
        cond0=float(geo.get("cond0", 1.0)),
        dX=float(geo.get("dX", 1e-6)),
        X_electrode=float(geo.get("X_electrode", 0.005)),
    )

    conditions = OperatingConditions(
        T0=float(cond.get("T0", 300.0)),
        Tenvironment=float(cond.get("Tenvironment", 293.15)),
        p=float(cond.get("p", 1.0)),
        voltage=float(data.get("voltage", -2.5)),
    )

    anode_rxn = _resolve_reaction(reac.get("anode", "OERdummy"))

    # Cathode may be a scalar string or a list (ammonia: [HERdummy, NRRdummy])
    cathode_raw = reac.get("cathode", "HERdummy")
    if isinstance(cathode_raw, list):
        resolved = [_resolve_reaction(r) for r in cathode_raw]
        cathode_rxn   = resolved[0]
        cathode_extra = resolved[1:] if len(resolved) > 1 else None
    else:
        cathode_rxn   = _resolve_reaction(cathode_raw)
        cathode_extra = None

    cathode_kind = str(reac.get("cathode_type", "planar"))

    anode = Electrode(
        reaction=anode_rxn,
        kappa=float(elec.get("kappa_anode", 75.0)),
    )
    cathode = Electrode(
        reaction=cathode_rxn,
        kappa=float(elec.get("kappa_cathode", 85.0)),
        kind=cathode_kind,
        extra_reactions=cathode_extra,
    )

    separator = Separator(kappa=float(diap.get("kappa", 38.0)))

    # Concentrations: flat list (AWE) or block dict (ammonia)
    raw_conc = data.get("concentrations", [])
    if isinstance(raw_conc, dict):
        raw_c0      = raw_conc.get("electrolyte", [])
        raw_c0_gas  = raw_conc.get("gas_channel", [])
    else:
        raw_c0      = raw_conc
        raw_c0_gas  = None

    raw_species = data.get("species", [])
    electrolyte = Electrolyte(
        species=[str(s) for s in raw_species],
        c0=[float(x) for x in raw_c0],
        mode=str(data.get("electrolyte_mode", "simple")),
    )

    # Gas channel block (ammonia only)
    gc_block = data.get("gas_channel", {})
    if gc_block:
        raw_mvf = gc_block.get("mol_vec_frac0", [])
        gas_channel_params = GasChannelParams(
            mol_vec_frac0=[float(x) for x in raw_mvf],
            c0_gas_channel=[float(x) for x in raw_c0_gas] if raw_c0_gas else [],
            slices=int(gc_block.get("slices", 10)),
            t=float(gc_block.get("t", 5.0)),
        )
    else:
        gas_channel_params = None

    return ReactorModel(
        name=data["name"],
        geometry=geometry,
        conditions=conditions,
        anode=anode,
        cathode=cathode,
        separator=separator,
        electrolyte=electrolyte,
        flow_channel=FlowChannel(),
        sim_stop_time=float(sim.get("stop_time", 50.0)),
        setup=str(data.get("setup", "continuous_0D_alkaline")),
        gas_channel_params=gas_channel_params,
    )


def parse(filepath: str) -> ReactorModel:
    """Parse a .reactor file and return a populated ReactorModel."""
    return _build_model(_parse_to_dict(filepath))