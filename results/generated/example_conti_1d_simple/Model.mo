within eCherry_Library.Examples.Continuous;
model AWE_Conti_1D_Simple
  import Echery_library = eCherry_Library;
  extends Modelica.Icons.Example;

  parameter Real Ufixed = -2.3;

  // ── Electrical ──────────────────────────────────────────────────────────────
  Modelica.Electrical.Analog.Basic.Ground Ground;
  Echery_library.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed Source(
    Ufixed = Ufixed,
    GeoRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec);

  // ── Anode ────────────────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Anode(
    specRec   = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.OERdummy},
    CathodeEl = false,
    P         = 100000,
    Pi(each displayUnit="bar"),
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Cathode ───────────────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Cathode(
    specRec   = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.HERdummy},
    CathodeEl = true,
    P         = 100000,
    Pi(each displayUnit="bar"),
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Bulk electrolyte compartments (0D, identical to continuous simple) ────────
  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Anolyte(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec      = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    CondRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.CondRec,
    c0          = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.c0,
    kappa_const = 75,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Catholyte(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec      = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    CondRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.CondRec,
    c0          = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.c0,
    kappa_const = 85,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Separator ─────────────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.Separators.Diaphragm_Hydroxide Diaphragm(
    specRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec  = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    CondRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.CondRec,
    kappa   = 38,
    X       = 5e-06,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Anode-side material flows ─────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed AnodeInflow(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    molFlow_vec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.c0 * 0.05);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow Flow_anode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Environment env_anode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec);

  // ── Cathode-side material flows ───────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed CathodeInflow(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    molFlow_vec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.c0 * 0.05);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow Flow_Cathode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Environment env_cathode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec);

  // ── Diffusion layers (1D boundary layer between electrode and bulk) ───────────
  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_1D_L_nLayers Diff_Anolyte(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec      = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    CondRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.CondRec,
    X_difflayer = 1e-06,
    c0          = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.c0,
    kappa_con   = 85,
    n_slices    = 10);

  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_1D_L_nLayers Diff_Catholyte(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec      = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    CondRec     = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.CondRec,
    X_difflayer = 1e-06,
    c0          = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.c0,
    kappa_con   = 74,
    n_slices    = 10);

  Echery_library.ElectrochemicalReactor.MaterialDomain.ConnectionLayers.ConnectionLayer_Diffusive ConnLayer_Anode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec  = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    dX      = 1e-07);

  Echery_library.ElectrochemicalReactor.MaterialDomain.ConnectionLayers.ConnectionLayer_Diffusive ConnLayer_Cathode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.AWEspec,
    GeoRec  = Echery_library.Data.UserInput.AWE_Conti_1D_Simple_UserInput.GeoRec,
    dX      = 1e-07);

equation
  // Electrical — diffusion layers inserted into the ionic chain
  connect(Ground.p,         Source.p);
  connect(Anode.p,          Source.n);
  connect(Source.p,         Diff_Catholyte.n);
  connect(Anode.n,          Diff_Anolyte.p);
  connect(Diff_Anolyte.n,   Anolyte.p);
  connect(Anolyte.n,        Diaphragm.p);
  connect(Diaphragm.n,      Catholyte.p);
  connect(Catholyte.n,      Diff_Catholyte.p);
  connect(Diff_Catholyte.n, Cathode.p);

  // Anode side — material (diffusion layer → connection layer → bulk)
  connect(Anode.flowFromElectrolyte,  Diff_Anolyte.leftFlow);
  connect(Diff_Anolyte.rightFlow,     ConnLayer_Anode.leftFlow);
  connect(ConnLayer_Anode.rightFlow,  Anolyte.leftFlow);
  connect(AnodeInflow.convFlow,       Anolyte.inFlow);
  connect(Anolyte.outFlow,            Flow_anode.convinFlow);
  connect(Flow_anode.convoutFlow,     env_anode.convFlow);
  connect(Anolyte.rightFlow,          Diaphragm.anCon);

  // Cathode side — material (bulk → connection layer → diffusion layer)
  connect(Diaphragm.catCon,            Catholyte.leftFlow);
  connect(CathodeInflow.convFlow,      Catholyte.inFlow);
  connect(Catholyte.outFlow,           Flow_Cathode.convinFlow);
  connect(Flow_Cathode.convoutFlow,    env_cathode.convFlow);
  connect(Catholyte.rightFlow,         ConnLayer_Cathode.leftFlow);
  connect(ConnLayer_Cathode.rightFlow, Diff_Catholyte.leftFlow);
  connect(Diff_Catholyte.rightFlow,    Cathode.flowFromElectrolyte);

  annotation(experiment(StopTime = 5));

end AWE_Conti_1D_Simple;
