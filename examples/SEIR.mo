model SEIR
Real S(start=1);
Real E(start=0);
Real I;
Real Mild, Severe, SevereH, Fatal;
Real R_Mild, R_Severe, R_Fatal;

parameter Real N(fixed=false) = 7e6;
parameter Real I0(fixed=false) = 1.;
parameter Real R0(fixed=false) = 2.2;
parameter Real Rt(fixed=false);
parameter Real D_incubation(fixed=false) = 5.2;
parameter Real D_infectious(fixed=false) = 2.9;
parameter Real CFR(fixed=false) = 0.02;

parameter Real Time_to_death(fixed=false) = 32;
parameter Real P_SEVERE(fixed=false) = 0.2;
parameter Real OMInterventionAmt(fixed=false) = 2./3;
parameter Real InterventionAmt(fixed=false);
parameter Real Intervention_time(fixed=false) = 100;
parameter Real duration(fixed=false) = 1e20;
parameter Real beta(fixed=false);
parameter Real a(fixed=false);
parameter Real _gamma(fixed=false);
parameter Real p_mild(fixed=false);
parameter Real p_severe(fixed=false);
parameter Real p_fatal(fixed=false);
parameter Real D_recovery_mild(fixed=false) = 11.1;
parameter Real D_recovery_severe(fixed=false) = 28.6; 
parameter Real D_death(fixed=false);
parameter Real D_hospital_lag(fixed=false) = 5;

initial algorithm
    InterventionAmt := 1. - OMInterventionAmt;
    a := 1./D_incubation;
    _gamma := 1./D_infectious;
    p_severe := P_SEVERE;
    p_fatal := CFR;
    p_mild := 1. - p_severe - p_fatal;
    D_death := Time_to_death - D_infectious;
    Rt := R0*InterventionAmt;
    beta := R0/D_infectious;

    I := I0/(N-I0);
    Mild := 0;
    Severe := 0;
    SevereH := 0;
    Fatal := 0;
    R_Mild := 0;
    R_Severe := 0;
    R_Fatal := 0;

equation
    der(S)         = -beta*I*S;
    der(E)         = beta*I*S - a*E;
    der(I)         = a*E - _gamma*I;
    der(Mild)      = p_mild*_gamma*I - Mild/D_recovery_mild;
    der(Severe)    = p_severe*_gamma*I - Severe/D_hospital_lag;
    der(SevereH)   = Severe/D_hospital_lag - SevereH/D_recovery_severe;
    der(Fatal)     = p_fatal*_gamma*I - Fatal/D_death;
    der(R_Mild)    = Mild/D_recovery_mild;
    der(R_Severe)  = SevereH/D_recovery_severe;
    der(R_Fatal)   = Fatal/D_death;


end SEIR;