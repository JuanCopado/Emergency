# PEDIATRIC OUTPATIENT — PORTUGAL / AZORES PRODUCT RECONCILIATION

Fecha: 04/10/2026
Rama: `v1.38-pediatric-outpatient-medications`

## Regla de interpretación

Esta tabla diferencia:
- **PT presentation documented**: INFARMED/RCM/AIM documentation supports that strength/form exists or has been authorised in Portugal.
- **PT historical/regulatory only**: documentation exists, but current marketing status is not established by the source used.
- **Azores stock unknown**: no static national source proves that a specific pharmacy/hospital in the Azores has stock today.

A documented Portuguese presentation is **not** permission to substitute concentrations. The exact dispensed product/RCM must be checked before calculating mL.

## Reconciled strengths/forms

| Drug / product family | Portuguese evidence found | Status for automatic arithmetic | Notes |
|---|---|---|---|
| Amoxicillin oral suspension | 125 mg/5 mL, 250 mg/5 mL, 500 mg/5 mL (25/50/100 mg/mL) in INFARMED documentation | **PT presentation documented** | Exact bottle/product still required. |
| Amoxicillin/clavulanate oral suspension | 400/57 mg per 5 mL (amoxicillin 80 mg/mL; clavulanate 11.4 mg/mL) documented by INFARMED | **PT presentation documented** | Do not substitute 250/62.5 or other ratios; clavulanate exposure changes. |
| Ibuprofen oral suspension | 20 mg/mL documented by INFARMED | **PT presentation documented** | 40 mg/mL not added to automatic registry without an exact current Portuguese product verification. |
| Azithromycin oral suspension | 40 mg/mL documented in INFARMED availability/stock-trace documentation | **PT presentation documented** | Matches 200 mg/5 mL arithmetic. |
| Cetirizine oral solution | 1 mg/mL documented by INFARMED / Zyrtec national documentation | **PT presentation documented** | Exact product and age licensing must still be checked. |
| Loratadine syrup | 1 mg/mL appears in recent INFARMED reimbursement documentation | **PT documentation found; market status recheck required** | Do not infer Azores stock. |
| Desloratadine oral solution | 0.5 mg/mL appears in recent INFARMED documentation | **PT documentation found; market status recheck required** | Do not infer Azores stock. |
| Mometasone nasal spray | 50 micrograms/dose in INFARMED national/mutual-recognition documentation | **PT presentation documented** | Use product-specific pediatric age indication. |
| Ketotifen eye drops | 0.25 mg/mL documented by INFARMED; Portuguese product/OTC protocol exists | **PT presentation documented** | One 2025 Zaditen lot was recalled; this does not imply class-wide withdrawal. Verify current product/lot. |
| Paracetamol oral solution | Apiretal 100 mg/mL received positive Portuguese AIM opinion in 2024; historic Ben-u-ron 40 mg/mL documentation also exists | **Exact current product must be verified** | The registry must not default from 24 mg/mL to 100 or 40 mg/mL. |
| Aciclovir oral suspension | 80 mg/mL appears in older Portuguese regulatory/pack-size documentation | **PT historical/regulatory only** | Current market availability not established by the evidence used. Keep external-product verification gate. |
| Oral rehydration salts | Electrolytes + glucose oral-solution powder appears in INFARMED availability documentation | **Product family documented** | Composition/osmolality must be checked against low-osmolarity ORS requirement. |

## Stock in Azores

The sources reviewed establish national regulatory/presentation information, not real-time pharmacy or hospital stock on Faial, Pico, São Miguel or other islands.

Therefore:
- `azores_stock_status = unknown` unless checked against a live local pharmacy/hospital inventory.
- the calculator must never choose a concentration because it is "common in Portugal";
- the user/prescriber must select the exact dispensed product or verify its RCM first.

## High-priority local reconciliation still pending

Before green review, verify via INFOMED/current local formulary:
1. paracetamol pediatric liquid(s);
2. amoxicillin 125/250/500 mg per 5 mL;
3. amoxicillin/clavulanate ratios actually stocked;
4. cefalexin pediatric suspension;
5. clarithromycin and azithromycin suspensions;
6. nitrofurantoin pediatric liquid;
7. trimethoprim/co-trimoxazole pediatric liquids;
8. oseltamivir suspension;
9. aciclovir suspension;
10. ondansetron oral liquid;
11. prednisolone/dexamethasone oral liquids;
12. pediatric ICS / ICS-formoterol inhaler devices;
13. epinephrine auto-injector strengths.

## Safety gate

Until that local check exists, a Portuguese documentation match may be shown as a candidate presentation, but **mL output still requires the exact product concentration selected by the clinician/pharmacist**.
