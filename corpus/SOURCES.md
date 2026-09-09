# Corpus Sources

Documents used as the retrieval corpus for this project.
Scope: shrimp/fish disease, water quality, and pond management.

Downloaded: 2026-09-08

---

## 1. ciba_2022_shrimp_culture_disease.pdf

- **Title:** Training Manual on Shrimp Culture and Disease Management in
  Inland Saline Areas
- **Series:** ICAR-CIBA TM Series 2022, No. 30
- **Publisher:** ICAR-Central Institute of Brackishwater Aquaculture, Chennai
- **Date:** December 2022
- **URL:** https://ciba.res.in/wp-content/uploads/2022/12/Final-Training-Manual-shrimp-culture-and-disease-managment_c.pdf
- **Covers:** seed selection, acclimatization, nursery rearing, grow-out
  production and management, biosecurity and farm-level disease management
  in *Penaeus vannamei*
- **License:** © 2022 by ICAR-CIBA, Chennai. Per the copyright page (p. ii):
  "Can be used by the stakeholders associated with the development of
  brackishwater aquaculture in India with due acknowledgement." Not a
  standard open license — attribution required, no explicit permission for
  redistribution outside India/non-stakeholders confirmed.
- **Pages:** 177

## 2. ciba_2021_ehp_management.pdf

- **Title:** Recent Advances on Diagnosis and Management of
  *Enterocytozoon hepatopenaei* (EHP) in Brackishwater Shrimp Aquaculture
- **Series:** ICAR-CIBA TM Series 2021, No. 23 (Revised Edition, 2022)
- **Publisher:** ICAR-CIBA, Aquatic Animal Health and Environment Division,
  Chennai
- **Date:** 2021, revised 2022
- **URL:** https://ciba.res.in/wp-content/uploads/2023/06/Manual_.pdf
  (official ciba.res.in copy — confirmed by title page text: "CIBA TM
  Series 2021 No. 23, Revised Edition, 2022 ... RECENT ADVANCES ON
  DIAGNOSIS AND MANAGEMENT OF Enterocytozoon hepatopenaei (EHP) IN
  BRACKISHWATER SHRIMP AQUACULTURE")
- **Covers:** EHP diagnosis and management, in depth (cited internally as
  102 pp; the PDF as downloaded has 110 pages including cover/front matter)
- **License:** All rights reserved. Per the disclaimer page: "No part of
  this publication may be reproduced, stored in a retrieval system or
  transmitted in any form or by any means ... without the prior written
  permission of Director, CIBA." Redistribution not permitted without
  CIBA's written permission.
- **Pages:** 110 (PDF page count; cited by the authors as "102 pp")

## 3. fao_1993_water_quality_fish_health.pdf

- **Title:** Water Quality and Fish Health
- **Series:** EIFAC Technical Paper No. 54 (ISBN 92-5-103437-0)
- **Authors:** Zdenka Svobodova, Richard Lloyd, Jana Machova, Blanka Vykusova
- **Publisher:** Food and Agriculture Organization of the United Nations, Rome
- **Date:** 1993
- **URL:** https://openknowledge.fao.org/server/api/core/bitstreams/185abd2a-fe7d-49dc-86ff-a6a1174566c7/content
  (PDF bitstream from FAO's Open Knowledge repository)
- **Format:** PDF, 71 pages
- **Covers:** water temperature, pH, dissolved oxygen thresholds; causes and
  effects of pollution on fish; diagnosis of fish poisoning; control of
  water quality
- **License:** © FAO 1993. Explicit notice on p. 2: "All rights reserved.
  No part of this publication may be reproduced, stored in a retrieval
  system, or transmitted ... without the prior permission of the copyright
  owner." Pre-dates FAO's modern CC BY-NC-SA 3.0 IGO default (introduced
  ~2013) — this document is traditional all-rights-reserved copyright, not
  open-licensed.
- **Note:** oldest document in the corpus. Retained for its numeric
  thresholds. Where it disagrees with newer sources, that disagreement is
  itself useful test material.
- **HTML edition also exists:** an 8-page multi-page HTML version of the
  same text is hosted at
  https://www.fao.org/fishery/docs/CDrom/aquaculture/a0844t/docrep/009/T1623E/T1623E00.htm
  (page 1 of that edition is a table-of-contents/frame page, not article
  text — a ~19 KB copy of it was pulled by mistake initially and has been
  deleted). Not downloaded for this phase; reserved as a Phase 2
  structure-chunking test case, since the HTML edition's per-page
  boundaries and heading structure differ from the PDF's layout.

## 4. mpeda_2003_shrimp_health_extension.pdf

- **Title:** Shrimp Health Management Extension Manual
- **Publisher:** MPEDA (Marine Products Export Development Authority),
  Cochin, in cooperation with NACA, Bangkok
- **Date:** 2003
- **URL:** https://library.enaca.org/Shrimp/manual/ShrimpHealthManual.pdf
- **Covers:** farm-level risk factors and practical management practices to
  reduce shrimp disease outbreaks. Based on a study conducted in
  Andhra Pradesh.
- **Audience:** small-scale and marginal farmers — plain language
- **License:** No copyright or license statement found anywhere in the
  document (checked title page, foreword, preface, acknowledgements, and
  bibliography — none present). Not confirmed Creative Commons despite
  NACA's general practice; treat as unconfirmed/all-rights-reserved by
  default until NACA/MPEDA confirms otherwise. Publicly hosted for free
  download via NACA's library (library.enaca.org).
- **Pages:** 46

---

## Candidates not yet included

- **MPEDA Shaphari certification guidelines (2021)** —
  https://mpeda.gov.in/wp-content/uploads/2021/02/Shaphari-C-of-F-guidelines.pdf
  Numbered-section structure. Useful when testing structure-aware chunking
  in Phase 2.
- **ICAR-CIBA, Risk Management Survey and Loss Assessment in Shrimp
  Farming (2024)** —
  https://ciba.res.in/wp-content/uploads/2024/11/Training-manual-LOSS-ASSESSMENT-IN-SHRIMP-FARMING.pdf
  Excluded initially: heavy topical overlap with document 1.

---

## Redistribution

Licensing has now been checked for all four documents — none are openly
licensed:

- Doc 1 (CIBA shrimp culture): usable with attribution by stakeholders in
  Indian brackishwater aquaculture; not a general open license.
- Doc 2 (CIBA EHP): all rights reserved, redistribution requires CIBA's
  written permission.
- Doc 3 (FAO): all rights reserved, pre-dates FAO's open-license era.
- Doc 4 (MPEDA/NACA): no license statement found; treated as
  all-rights-reserved by default.

Given this, the source files are gitignored and only this file is
committed. Anyone reproducing this work should download from the URLs
above rather than redistributing the local copies.
