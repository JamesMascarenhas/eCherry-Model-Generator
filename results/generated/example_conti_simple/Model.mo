within eCherry_Library.Examples.Continuous;
model AWE_Conti_Simple
  import Echery_library = eCherry_Library;
  extends Modelica.Icons.Example;

  parameter Real Ufixed = -2.5;

  // Electrical ground and voltage source
  Modelica.Electrical.Analog.Basic.Ground Ground;

  Echery_library.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed Source(
    Ufixed = Ufixed,
    GeoRec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.GeoRec);

  // Electrodes
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Anode(
    specRec   = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.OERdummy},
    CathodeEl = false,
    P         = 100000,
    Pi(each displayUnit="bar"),
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Cathode(
    specRec   = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.HERdummy},
    CathodeEl = true,
    P         = 100000,
    Pi(each displayUnit="bar"),
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // Electrolyte compartment(s)
  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Anolyte(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec,
    GeoRec      = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.GeoRec,
    CondRec     = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.CondRec,
    c0          = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.c0,
    kappa_const = 75,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Catholyte(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec,
    GeoRec      = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.GeoRec,
    CondRec     = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.CondRec,
    c0          = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.c0,
    kappa_const = 85,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // Separator
  Echery_library.ElectrochemicalReactor.Separators.Diaphragm_Hydroxide Diaphragm(
    specRec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec,
    GeoRec  = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.GeoRec,
    CondRec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.CondRec,
    kappa   = 38,
    X       = 0.0005,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // Anode-side material flows
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed AnodeInflow(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec,
    molFlow_vec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.c0 * 0.005);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow Flow_anode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Environment env_anode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec);

  // Cathode-side material flows
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed CathodeInflow(
    specRec     = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec,
    molFlow_vec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.c0 * 0.005);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow Flow_Cathode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Environment env_cathode(
    specRec = Echery_library.Data.UserInput.AWE_Conti_Simple_UserInput.AWEspec);

equation
  // Electrical
  connect(Ground.p,  Source.p);
  connect(Anode.p,   Source.n);
  connect(Source.p,  Cathode.n);

  // Anode side — material flow
  connect(AnodeInflow.convFlow,   Anolyte.inFlow);
  connect(Anolyte.outFlow,        Flow_anode.convinFlow);
  connect(Flow_anode.convoutFlow, env_anode.convFlow);
  // Anode side — electrode coupling and separator
  connect(Anolyte.leftFlow,  Anode.flowFromElectrolyte);
  connect(Anode.n,           Anolyte.p);
  connect(Anolyte.rightFlow, Diaphragm.anCon);
  connect(Anolyte.n,         Diaphragm.p);

  // Cathode side — material flow
  connect(CathodeInflow.convFlow,    Catholyte.inFlow);
  connect(Catholyte.outFlow,         Flow_Cathode.convinFlow);
  connect(Flow_Cathode.convoutFlow,  env_cathode.convFlow);
  // Cathode side — electrode coupling and separator
  connect(Catholyte.rightFlow, Cathode.flowFromElectrolyte);
  connect(Cathode.n,          Catholyte.p);
  connect(Catholyte.leftFlow, Diaphragm.catCon);
  connect(Catholyte.n,        Diaphragm.n);

  annotation(experiment(StopTime = 50));

end AWE_Conti_Simple;