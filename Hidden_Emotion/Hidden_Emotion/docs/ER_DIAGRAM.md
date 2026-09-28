# Entity Relationship Diagram (ERD)

```
 +------------------------+             +------------------------+
 |        USERS           |             |       DOCUMENTS        |
 +------------------------+             +------------------------+
 | _id (PK)               | 1         * | doc_id (PK)            |
 | user_id                |------------<| filename               |
 | username               |             | doc_type               |
 | email                  |             | word_count             |
 | password               |             | uploaded_by (FK)       |
 | role (user/admin)      |             | uploaded_at            |
 +------------------------+             +------------------------+
             |                                      |
             | 1                                    | 1
             |                                      |
             v *                                    v *
 +------------------------+             +------------------------+
 |      PREDICTIONS       |             |        HISTORY         |
 +------------------------+             +------------------------+
 | report_id (PK)         |             | report_id (PK)         |
 | doc_id (FK)            |             | user_id (FK)           |
 | user_id (FK)           |             | filename               |
 | primary_emotion        |             | primary_emotion        |
 | hidden_emotion         |             | primary_intent         |
 | primary_intent         |             | report_data (JSON)     |
 | confidence             |             | created_at             |
 | report_data (JSON)     |             +------------------------+
 +------------------------+
```
