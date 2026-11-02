# Scratchpad

## Backend access (recorded 2026-11-02)

Participants will have access to the following Quantinuum backends throughout the challenge:
- H2-1
- H2-2
- Helios-1
- Helios-1E

Each team has been allocated **8000 HQCs** for use on H2-1 and H2-2.

Helios-1 and Helios-1E are available at low priority: expect longer queue times. Results
submitted to either Helios machine during the final few days of the challenge are not
guaranteed to complete, so submit jobs early.

Continued access to existing systems, as normal:
- H2-1
- H2-2
- H2-Emulator
- Selene

## HQC estimates of our programs (formula, not Quantinuum's price)

HQC = 5 + shots · (N1q + 10·N2q + 5·Nm) / 5000. Range: N1q = phasedx only .. phasedx + rz.

| program | shots | HQC |
| --- | --- | --- |
| d3, R = 2 (p 0 or 0.05) | 100 | 15–17 |
| d5, Δt = 5 (R = 2) | 1000 | 318–380 |
| d5, Δt = 2.5 (R = 4) | 1000 | 597–710 |
| d5, Δt = 1 (R = 10) | 1000 | 1432–1700 |
| d5, Δt = 0.5 (R = 20) | 1000 | 2824–3350 |
| d5, Δt = 0.14 (R = 70) | 1000 | 9784–11600 |

aqora's earlier "cost exceeds allowed cost (1002)" did not match this formula (R = 20 was accepted).
Exact price: `hardware.cli nexus-cost <program>.bc --shots N`.
