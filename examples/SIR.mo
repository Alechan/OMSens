model SIR
  parameter Real beta=0.6;
  parameter Real gamma=0.06;
  
  parameter Real total = 4500;
  parameter Real infected_init=1;
  parameter Real susceptible_init=total - infected_init;
  parameter Real recovered_init=0;
  
  Real susceptible(start=susceptible_init);
  Real infected(start=infected_init);
  Real recovered(start=susceptible_init);
  Real max_infected(start=0);

initial equation
  susceptible = susceptible_init;
  infected    = infected_init;
  recovered   = recovered_init;
equation
  der(susceptible) = -susceptible*infected*beta/total;
  der(infected)    = susceptible*infected*beta/total - infected*gamma;
  der(recovered)   = infected*gamma;
  
  max_infected = max(infected, pre(max_infected));

annotation(
    __OpenModelica_simulationFlags(ls = "klu", lv = "LOG_STATS", s = "irksco"));end SIR;