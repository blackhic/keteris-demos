# Gabarits de maquettes Keteris (PME 20-500 salariés)
- app.html : gabarit unique piloté par un bloc JSON (vues : table, pipeline, dashboard). Ne pas modifier pour un prospect.
- exemples/<segment>.json : un exemple complet par segment (cabinets_relances, adv_pipeline, encaissement, devis_relance, tableau_direction).
- fabriquer.py : `python3 _gabarits/fabriquer.py <slug> <donnees.json>` → <slug>/index.html + <slug>/apercu.png, avec contrôle bureau/mobile.
