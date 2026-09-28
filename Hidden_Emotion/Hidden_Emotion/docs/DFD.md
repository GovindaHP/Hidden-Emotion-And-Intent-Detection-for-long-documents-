# Data Flow Diagrams (DFD)

## Level 0 Context Diagram

```
 +-------------+       Uploaded File / Text Input      +---------------------------------+
 |             | ------------------------------------> |                                 |
 |    User     |                                       |   Hidden Emotion & Intent       |
 |             | <------------------------------------ |   Detection AI System           |
 +-------------+   AI Psychological & Intent Report    +---------------------------------+
```

---

## Level 1 Data Flow Diagram

```
                        +----------------------------------+
                        |  1.0 Authentication & Access     |
                        +----------------------------------+
                                      |
                                      v
                        +----------------------------------+       Stored Document
  User Input ---------> |  2.0 File & Text Extraction      | ----------------------> [ Documents Store ]
                        +----------------------------------+
                                      |
                                      v
                        +----------------------------------+
                        |  3.0 Cleaning & Semantic Chunker |
                        +----------------------------------+
                                      |
                                      v
                        +----------------------------------+
                        |  4.0 Embedder & Emotion Engine   |
                        +----------------------------------+
                                      |
                                      v
                        +----------------------------------+       Prediction Report
                        |  5.0 Intent & Summary Pipeline   | ----------------------> [ Predictions Store ]
                        +----------------------------------+
                                      |
                                      v
                        +----------------------------------+
                        |  6.0 Report Generator & Visuals  | --------> User Report View
                        +----------------------------------+
```
