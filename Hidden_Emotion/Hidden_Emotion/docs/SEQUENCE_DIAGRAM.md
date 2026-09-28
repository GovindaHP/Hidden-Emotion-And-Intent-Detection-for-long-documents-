# Sequence Diagrams

## Document Analysis Sequence Diagram

```
User (Browser)               FastAPI Backend              NLP Engine              Database
      |                             |                         |                      |
      |--- 1. POST /upload -------->|                         |                      |
      |    (File + Document Type)   |                         |                      |
      |                             |--- 2. Extract Text ---->|                      |
      |                             |    & Preprocess         |                      |
      |                             |                         |                      |
      |                             |--- 3. Semantic Chunking>|                      |
      |                             |    & Embeddings         |                      |
      |                             |                         |                      |
      |                             |--- 4. Emotion, Intent ->|                      |
      |                             |    Summarization, NER   |                      |
      |                             |                         |                      |
      |                             |<-- 5. Complete Report --|                      |
      |                             |                         |                      |
      |                             |--- 6. Save Record --------------------------->|
      |                             |                                                |
      |<-- 7. Report JSON Output ---|                                                |
      |                             |                                                |
```
