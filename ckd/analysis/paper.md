

# CKD ICER AND QALY methodology


# ICER (Incremental Cost-Effectiveness Ratio) and QALY (Quality-Adjusted Life Years) Methodology

## Quality-Adjusted Life Years (QALY) Formula

### Basic QALY Formula
QALY = Utility Score × Life Years

Where:
- Utility Score: Health-related quality of life measure ranging from 0 (death) to 1 (perfect health)
- Life Years: Number of years lived in a particular health state

### QALY Formula for Multiple Time Periods
$$QALY_{total} = \sum_{t=0}^{T} U_t$$

Where:
- U_t: Utility score at time t
- t: Time period (usually years)
- T: Total time horizon

### CKD-Specific QALY Considerations
For chronic kidney disease patients, QALYs are calculated considering progression through different stages:

$$QALY_{CKD} = \sum_{s=1}^{5} U_s \times Y_s$$

Where:
- $U_s$: Utility score for CKD stage s
- $Y_s$: Years spent in CKD stage s

## Incremental Cost-Effectiveness Ratio (ICER) Formula

### Basic ICER Formula
ICER = (C_intervention - C_control) / (E_intervention - E_control)

Or expressed as:
ICER = ΔC / ΔE

Where:
- C_intervention: Total cost of intervention strategy
- C_control: Total cost of control/standard care strategy
- E_intervention: Health outcomes (typically QALYs) in intervention group
- E_control: Health outcomes (typically QALYs) in control group
- ΔC: Incremental cost (difference in costs)
- ΔE: Incremental effectiveness (difference in health outcomes)

### ICER Interpretation
- ICER < $50,000/QALY: Generally considered cost-effective
- ICER $50,000-$100,000/QALY: Moderately cost-effective
- ICER > $100,000/QALY: Less likely to be cost-effective
- Negative ICER with positive ΔE: Dominant strategy (cost-saving and more effective)
- Positive ICER with negative ΔE: Dominated strategy (more costly and less effective)

## Cost Components for CKD Economic Evaluation

### Direct Medical Costs
- Healthcare provider visits (nephrologist, primary care)
- Laboratory tests and monitoring
- Medications (ACE inhibitors, ARBs, phosphate binders, etc.)
- Dialysis treatment costs
- Kidney transplantation costs
- Hospitalization costs
- Emergency department visits

### Indirect Costs
- Productivity losses due to illness
- Caregiver time and costs
- Transportation costs for medical care

## Utility Values for CKD Stages (Literature-Based)

### Commonly Reported Utility Values
- Healthy population: 1.00
- CKD Stage 1: 0.95 (95% of perfect health)
- CKD Stage 2: 0.90
- CKD Stage 3a: 0.85
- CKD Stage 3b: 0.80
- CKD Stage 4: 0.65
- CKD Stage 5 (pre-dialysis): 0.45
- Hemodialysis: 0.40
- Peritoneal dialysis: 0.42
- Kidney transplant: 0.85

## Markov Model Framework for CKD Progression

### State Transition Probabilities
The economic model typically uses Markov chains to model CKD progression:

P(t+1) = P(t) × M

Where:
- P(t): Probability distribution across health states at time t
- M: Transition probability matrix between CKD stages

### Expected Value Calculation
Expected Cost = Σ(s=1 to n) [π_s × C_s]
Expected QALY = Σ(s=1 to n) [π_s × U_s]

Where:
- π_s: Probability of being in state s
- C_s: Cost associated with state s
- U_s: Utility associated with state s
- n: Number of health states

## Sensitivity Analysis Considerations

### Deterministic Sensitivity Analysis
- One-way sensitivity analysis: Vary one parameter at a time
- Two-way sensitivity analysis: Vary two parameters simultaneously
- Threshold analysis: Identify break-even points

### Probabilistic Sensitivity Analysis
- Monte Carlo simulation with parameter distributions
- Cost-effectiveness acceptability curves
- Expected value of perfect information (EVPI)

## Time Horizon and Discounting

### Recommended Practices
- Time horizon: Lifetime for chronic conditions like CKD
- Discount rate: 3% annually for both costs and outcomes (varies by country)
- Half-cycle correction: Adjust for timing of events within cycles

### Present Value Calculations
PV = FV / (1 + r)^t

Where:
- PV: Present value
- FV: Future value
- r: Discount rate
- t: Time period

