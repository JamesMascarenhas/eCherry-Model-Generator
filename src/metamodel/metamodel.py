from dataclasses import dataclass, field


@dataclass
class GeometryParams:
    X: float = 0.01
    X_membrane: float = 0.0005
    Y: float = 1.0
    Z: float = 1.0
    cond0: float = 1.0
    dX: float = 1e-6
    X_electrode: float = 0.005   # ammonia only — GeoRecElec.X; ignored by AWE families


@dataclass
class OperatingConditions:
    T0: float = 300.0
    Tenvironment: float = 293.15
    p: float = 1.0
    voltage: float = -2.5
    inflow_scale: float = 0.005


@dataclass
class Electrode:
    reaction: str
    kappa: float
    kind: str = "planar"
    extra_reactions: list[str] | None = None  # ammonia cathode only (e.g. ["NRRdummy"])


@dataclass
class Separator:
    kind: str = "hydroxide_diaphragm"
    kappa: float = 38.0


@dataclass
class Electrolyte:
    species: list[str]
    c0: list[float]
    mode: str = "simple"


@dataclass
class FlowChannel:
    mode: str = "simple_fixed"


@dataclass
class GasChannelParams:
    """Ammonia-specific gas channel parameters. None for all AWE families."""
    mol_vec_frac0: list[float]
    c0_gas_channel: list[float]
    slices: int = 10
    t: float = 5.0


@dataclass
class ReactorModel:
    name: str
    geometry: GeometryParams
    conditions: OperatingConditions
    anode: Electrode
    cathode: Electrode
    separator: Separator
    electrolyte: Electrolyte
    flow_channel: FlowChannel
    sim_stop_time: float = 50.0
    setup: str = "continuous_0D_alkaline"
    gas_channel_params: GasChannelParams | None = None  # ammonia only