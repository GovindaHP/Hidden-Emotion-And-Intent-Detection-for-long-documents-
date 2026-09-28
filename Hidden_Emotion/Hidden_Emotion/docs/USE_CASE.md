# Use Case Specifications

## Actors
1. **Registered User / Reader**: Uploads long documents, runs AI emotion & intent analysis, views visual analytics, searches history, and exports PDF/JSON/CSV reports.
2. **Administrator**: Manages registered accounts, inspects system logs, monitors engine status, and views aggregate usage metrics.

---

## Use Case Overview

```
                      +---------------------------------------+
                      |       Document AI System              |
                      |                                       |
                      |   (UC-1: Authenticate / JWT Login)    |
   [ User ] --------> |                                       | <-------- [ Administrator ]
      |               |   (UC-2: Upload Document File)        |                 |
      |               |   (UC-3: Paste Long Text)             |                 |
      +-------------> |   (UC-4: Generate AI Analysis Report) |                 |
      |               |   (UC-5: View Emotional Timeline)     |                 |
      |               |   (UC-6: Export PDF / JSON / CSV)     |                 |
      |               |   (UC-7: Search Prediction History)   |                 |
      |               |                                       |                 |
                      |   (UC-8: Manage System Users) <-------------------------+
                      |   (UC-9: Inspect System Logs) <-------------------------+
                      +---------------------------------------+
```
