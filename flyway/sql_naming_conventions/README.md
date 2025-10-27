TinMan SQL Naming Conventions
=========

Gives structure to databases with heart.

This document outlines which naming conventions from the style guide can or cannot currently be enforced using SQLFluff, and provides configuration settings for enforceable rules. This ruleset is a extension and merger of three different rulesets for SQL tables:

* [https://x.com/sehrope](https://x.com/sehrope) wrote [How I Write SQL, Part 1: Naming Conventions](https://launchbylunch.com/posts/2014/Feb/16/sql-naming-conventions/). When clarity is needed on how to use these, start here.
* [DURC](https://github.com/ftrotter/durc_is_crud) naming conventions
* [SQLFluff default rules](https://docs.sqlfluff.com/en/stable/configuration/default_configuration.html)

We intend to write additional sqlfluff rules to support the rules that sqlfluff does not already support when possible. eventually. given infinite time and resources.

⸻

Rules Not Currently Enforceable by SQLFluff
------

These require either a custom rule, external linter, or manual review:

* Use full English words, not abbreviations (so international_business_machines and not ibm)
* Don’t use data types as names (so sales_count and not sales_count_int. Let the INT data type say it is an integer)
* Use singular nouns for table names (person and not persons or people)
* Primary key fields that are simple identifiers should be named simply id
* Refrain from repeating the table name in the field name, if possible (e.g. if the table is called `person`, a phone number field within that table can be `phone` and shouldn't be `person_phone`)
* Foreign keys should follow the pattern `<table_name_here>_id`
  * Two foreign keys in the table requires a prefix on the foreign key column, to differentiate the two links. Like `<helpful_name>_<table_name_here>_id` etc.
  * Foreign keys can and should be created dynamically based on this naming convention.
* When there is a junction table, use the pattern `<table1_name>_to_<table2_name>`
* Name indexes explicitly with table and column ( fk_npiidentifier_npi_id and not fk_identifiers_need_keys)
* Name constraints clearly (uq_interop_endpoint_url and not uq_intendu)
* The varchar or text field listed first in the table is assumed to be the "auto-suggest search" field for the table. If this is not correct, then the table needs an explicit select_name field or postfixed field.
* DURC Reserved names:
  * a column named select_name or that ends in \_select_name is reserved for the field that will power an auto-suggest lookup on the table.
  * column names with a postfix of _markdown are used to invoke a front-end markdown editor
  * column names with a postfix of _code will invoke a code-editor on the front end.

⸻

Rules Enforceable by SQLFluff
------

These can be configured using standard SQLFluff rules:
* Avoid quoted identifiers → L014: Discourages use of quoted identifiers.
* Use all lowercase for identifiers → L010: Enforces case on keywords and identifiers.
* Use underscores to separate words (snake_case) → L040: Enforces naming convention patterns.
* Avoid reserved words as identifiers → L036: Detects use of reserved keywords as identifiers.

⸻

How to run
----
I suggest for now that people use the [VS Code sqlfluff linter to help using this for now](https://marketplace.visualstudio.com/items?itemName=dorzey.vscode-sqlfluff).
Further automations might happen with github actions later on.

[.sqlfluff](.sqlfluff) Configuration
----

This is a starting point and will change over time.


```conf
[sqlfluff]
dialect = postgres

[sqlfluff:rules]
exclude_rules = L009  # Optional: skip alias prefixing if undesired

[sqlfluff:rules:L010]
capitalisation_policy = lower  # Force lowercase for identifiers

[sqlfluff:rules:L014]
extended_capitalisation_policy = lower  # Reinforce lowercase for quoted identifiers
ignore_words = ''  # Do not allow any exceptions

[sqlfluff:rules:L036]
# No config needed — enabled by default


[sqlfluff:rules:capitalisation.keywords]
# Keywords
capitalisation_policy = upper

[sqlfluff:rules:L040]
capitalisation_policy = upper
naming_convention = snake_case
```
