within eCherry_Library.Examples.Batch.Batch0D;
model AWE_Batch_KOH
  import Echery_library = eCherry_Library;
  extends Modelica.Icons.Example;

  parameter Real Ufixed = -2.5;

  // Electrical ground and voltage source
  Modelica.Electrical.Analog.Basic.Ground Ground;

  Echery_library.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed Source(
    Ufixed = Ufixed,
    GeoRec = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.GeoRec,
    Y = 1,
    Z = 1);

  // Electrodes
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Anode(
    specRec   = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.OERdummy},
    CathodeEl = false,
    P         = 100000,
    Pi(each displayUnit="bar"),
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Cathode(
    specRec   = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.HERdummy},
    CathodeEl = true,
    P         = 100000,
    Pi(each displayUnit="bar"),
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // Electrolyte compartment(s)
  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_0D_L Electrolyte(
    specRec = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.AWEspec,
    GeoRec  = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.GeoRec,
    CondRec = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.CondRec,
    c0      = Echery_library.Data.UserInput.AWE_Batch_KOH_UserInput.c0,
    X       = 0.01,
    Y       = 1,
    Z       = 1,
    redeclare model ConductivityModel = eCherry_Library.ElectrochemicalReactor.Properties.ConductivityModels.ConductivityElectrolyteCalcKOH,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

equation
  // Electrical
  connect(Ground.p,  Source.p);
  connect(Anode.p,   Source.n);
  connect(Source.p,  Cathode.n);

  // Single shared electrolyte — electrode coupling
  connect(Anode.n,                    Electrolyte.p);
  connect(Electrolyte.n,              Cathode.p);
  connect(Cathode.flowFromElectrolyte, Electrolyte.rightFlow);
  connect(Electrolyte.leftFlow,        Anode.flowFromElectrolyte);


  annotation(experiment(StopTime = 50));

end AWE_Batch_KOH;