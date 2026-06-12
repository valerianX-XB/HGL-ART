# V5.5.1 Building Classification QA

| # | Test | Result | Evidence |
|---:|---|---|---|
| 1 | Peter Cooper Village / StuyTown is no longer broadly classified as office | PASS | StuyTown/Peter Cooper bbox residential-unit buildings: 462; eligible: 455; office-excluded: 0. |
| 2 | Large apartment complexes are not incorrectly excluded | PASS | Large (UnitsRes>=50) buildings in target ZIPs: 565; eligible: 518. |
| 3 | Office-only buildings remain excluded | PASS | Office-only excluded buildings with UnitsRes=0: 666. |
| 4 | Schools / universities remain excluded | PASS | School/university excluded buildings: 169. |
| 5 | Hotels / transient lodging remain excluded | PASS | Hotel/transient lodging excluded buildings: 181. |
| 6 | Hospitals / senior / institutional housing remain excluded | PASS | Medical/senior/shelter institutional exclusions: 55. |
| 7 | Mixed-use residential buildings remain eligible | PASS | Mixed-use family-residential eligible buildings: 3892. |
| 8 | All buildings still appear in 3D | PASS | Building massing layer still uses all visual building features; excluded buildings retain physical height as neutral context. |
| 9 | Build passes | PASS | `npm run build` completed successfully; see `logs_v5_5_1_build.log`. |

## Added classification fields
`classification_source_priority`, `classification_confidence`, `residential_evidence_score`, `exclusion_evidence_score`, `conflict_flag`, and `conflict_notes` are present on patched building features.