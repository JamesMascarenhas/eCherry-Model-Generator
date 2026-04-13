within eCherry_Library.Data.UserInput;

record AAE_Conti_Ammonia_UserInput
  import DataRecords = eCherry_Library.Data.DataRecords;

  // AESspec = Ammonia Electrochemical Synthesis Species
  constant eCherry_Library.Data.DataRecords.Species.SpeciesRecord AESspec(
    species = {
      eCherry_Library.Data.DataRecords.Species.GaseousSpecies.O2,
      eCherry_Library.Data.DataRecords.Species.GaseousSpecies.H2,
      eCherry_Library.Data.DataRecords.Species.GaseousSpecies.N2,
      eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.NH3,
      eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.OHm,
      eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.Kp,
      eCherry_Library.Data.DataRecords.Species.LiquidSpecies.H2O
    });

  // Reactions
  constant DataRecords.ElecReaction.Reaction NRRdummy = DataRecords.ElecReaction.List_Of_Reactions.NRRdummy;
  constant DataRecords.ElecReaction.Reaction HERdummy = DataRecords.ElecReaction.List_Of_Reactions.HERdummy;
  constant DataRecords.ElecReaction.Reaction OERdummy = DataRecords.ElecReaction.List_Of_Reactions.OERdummy;

  // Discretization — declared before geometry records that reference it
  constant Integer slices(min = 2) = 10;

  // Geometry: bulk / gas channel / anode side
  constant DataRecords.Geometry GeoRec(
    X          = 0.001,
    X_membrane = 0.000115,
    Y          = 0.5,
    Z          = 1/slices,
    cond0      = 1,
    dX         = 0.01);

  // Geometry: membrane
  constant DataRecords.Geometry GeoRecMem(
    X          = 0.000115,
    X_membrane = 0.000115,
    Y          = 0.5,
    Z          = 1/slices,
    cond0      = 1,
    dX         = 0.01);

  // Geometry: electrode / electrolyte
  constant DataRecords.Geometry GeoRecElec(
    X          = 0.005,
    X_membrane = 0.000115,
    Y          = 0.5,
    Z          = 1/slices,
    cond0      = 1,
    dX         = 0.01);

  // Conditions
  constant DataRecords.Conditions CondRec(
    T0           = 333.15,
    Tenvironment = 288.15,
    p            = 100000);

  // Concentrations: O2, H2, N2, NH3, OHm, Kp, H2O
  constant Modelica.Units.SI.Concentration c0_Electrolyte[AESspec.nSpec] = {0, 1.45e-12, 0, 0, 6000, 6000, 55000};
  constant Modelica.Units.SI.Concentration c0_GasChannel[AESspec.nSpec]  = {0, 0, 1, 0, 0, 0, 0};
  constant Real mol_vec_frac0[AESspec.nSpec] = {0, 0, 1, 0, 0, 0, 0};

  // Residence time in flow channel [s]
  constant Modelica.Units.SI.Time t = 5;

end AAE_Conti_Ammonia_UserInput;

