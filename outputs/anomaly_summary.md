# Anomaly Detection Summary
This report summarizes cattle anomaly detection based on milk yield, feed intake, THI, weight and age.
## Severity counts
- Normal: 584
- Warning: 2395
- Critical: 21

## Key findings
- Extreme heat stress cases: 2146
- Abnormal yield drop cases: 301
- Abnormal feed behaviour cases: 618
- Critical cases with extreme heat stress: 13

## Top critical cases
feature summary for top critical cases:
| Cattle_ID | milk_output | feed | thi | weight | age | issue_tags |
|---|---|---|---|---|---|---|
| COW00126 | 13.77 | 29.90 | 107.3 | 362.5 | 20 | extreme heat stress, abnormal yield drop |
| COW01971 | 12.95 | 20.30 | 118.3 | 662.3 | 111 | extreme heat stress, abnormal yield drop |
| COW00618 | 13.75 | 29.40 | 84.1 | 377.5 | 18 | extreme heat stress, abnormal yield drop |
| COW00706 | 27.52 | 30.20 | 76.5 | 775.0 | 12 | model anomaly |
| COW01493 | 11.69 | 22.90 | 69.5 | 348.7 | 47 | abnormal yield drop |
| COW02321 | 13.55 | 31.30 | 90.3 | 401.8 | 15 | extreme heat stress, abnormal yield drop, abnormal feed behaviour |
| COW01150 | 14.77 | 21.30 | 124.8 | 416.6 | 51 | extreme heat stress, abnormal yield drop |
| COW02016 | 13.97 | 26.60 | 110.4 | 379.0 | 56 | extreme heat stress, abnormal yield drop |
| COW02859 | 28.93 | 15.80 | 85.0 | 791.9 | 60 | extreme heat stress, abnormal feed behaviour |
| COW01537 | 27.24 | 31.20 | 69.7 | 736.5 | 23 | abnormal feed behaviour |
