## mcFail

python version of the copehiemer tool, developed by the 5c
found server will be analysed and the users inside the server collected if possible

mcFail sets up a sqlite database automatically in the projects root directory with the following schemas:

| Column | Type | Constraints           |
| ------ | ---- | --------------------- |
| uuid   | TEXT | NOT NULL, PRIMARY KEY |
| name   | TEXT | NOT NULL              |

| Column      | Type    | Constraints               |
| ----------- | ------- | ------------------------- |
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT |
| address     | TEXT    | NOT NULL                  |
| slots       | INTEGER | NOT NULL                  |
| online      | INTEGER | NOT NULL                  |
| version     | TEXT    | NOT NULL                  |
| description | TEXT    | NOT NULL                  |
| motd        | TEXT    | NOT NULL                  |

| Column     | Type     | Constraints                     |
| ---------- | -------- | ------------------------------- |
| player\_id | TEXT     | NOT NULL                        |
| server\_id | INTEGER  | NOT NULL                        |
| time       | DATETIME | NOT NULL, DEFAULT CURRENT\_TIME |

