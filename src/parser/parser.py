from src.metamodel.metamodel import (
    ReactorModel,
    GeometryParams,
    OperatingConditions,
    Electrode,
    Separator,
    Electrolyte,
    FlowChannel,
)

_REACTION_MAP = {
    "OER": "OERdummy",
    "OERdummy": "OERdummy",
    "HER": "HERdummy",
    "HERdummy": "HERdummy",
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


def _build_model(data: dict) -> ReactorModel:
    """Construct a ReactorModel from the intermediate dict."""
    geo = data.get("geometry", {})
    cond = data.get("conditions", {})
    elec = data.get("electrolyte", {})
    diap = data.get("diaphragm", {})
    reac = data.get("reactions", {})
    sim = data.get("simulation", {})

    geometry = GeometryParams(
        X=float(geo.get("X", 0.01)),
        X_membrane=float(geo.get("X_membrane", 0.0005)),
        Y=float(geo.get("Y", 1.0)),
        Z=float(geo.get("Z", 1.0)),
        cond0=float(geo.get("cond0", 1.0)),
        dX=float(geo.get("dX", 1e-6)),
    )

    conditions = OperatingConditions(
        T0=float(cond.get("T0", 300.0)),
        Tenvironment=float(cond.get("Tenvironment", 293.15)),
        p=float(cond.get("p", 1.0)),
        voltage=float(data.get("voltage", -2.5)),
    )

    anode_rxn = _REACTION_MAP.get(str(reac.get("anode", "OERdummy")), "OERdummy")
    cathode_rxn = _REACTION_MAP.get(str(reac.get("cathode", "HERdummy")), "HERdummy")

    anode = Electrode(
        reaction=anode_rxn,
        kappa=float(elec.get("kappa_anode", 75.0)),
    )
    cathode = Electrode(
        reaction=cathode_rxn,
        kappa=float(elec.get("kappa_cathode", 85.0)),
    )

    separator = Separator(kappa=float(diap.get("kappa", 38.0)))

    raw_species = data.get("species", [])
    raw_c0 = data.get("concentrations", [])
    electrolyte = Electrolyte(
        species=[str(s) for s in raw_species],
        c0=[float(x) for x in raw_c0],
        mode=str(data.get("electrolyte_mode", "simple")),
    )

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
    )


def parse(filepath: str) -> ReactorModel:
    """Parse a .reactor file and return a populated ReactorModel."""
    return _build_model(_parse_to_dict(filepath))
