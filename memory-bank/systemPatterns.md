# System Patterns

## Dataset Units

Each independent dataset should have a dataset ID and metadata. Raw storage may remain in legacy paths until a dedicated migration phase updates consumers.

## Highest Resolution Rule

If M1 data exists for the same instrument, provider, timezone, schema, and data semantics, coarser timeframes should be treated as derived views rather than separately stored source datasets.

Exceptions require documented evidence, such as different provider, session/calendar semantics, timestamp definition, additional fields, or other irreducible differences.

## Semantic Preservation

Do not alter timestamp units, timezone, bid/ask meaning, or CSV schema during structural refactors.

