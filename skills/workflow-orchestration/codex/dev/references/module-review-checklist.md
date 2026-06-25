# Module Review Checklist

Use this after each completed module and again before final handoff.

## Logic Health

- Does the implementation satisfy the module's acceptance criteria?
- Are edge cases handled, not only the happy path?
- Are state transitions explicit and consistent?
- Are API and UI assumptions aligned?
- Are time, pagination, sorting, filtering, and null cases handled where relevant?

## Redundancy And Structure

- Is there duplicated business logic that should be shared locally?
- Is there redundant state that can drift?
- Did the change create parallel models, clients, validators, or constants?
- Are helpers small enough to understand and large enough to justify existing?
- Is any new abstraction solving a real current problem?

## Error Handling

- Are errors surfaced at the right boundary?
- Are user-facing errors understandable?
- Are logs useful without leaking secrets or private data?
- Are retries, fallbacks, and empty states appropriate?

## Data And Contracts

- Are schemas, request/response types, DB models, and UI clients consistent?
- Are migrations reversible or at least locally testable?
- Are validation rules enforced server-side?
- Are defaults explicit?

## Security And Permissions

- Is authorization enforced at the server boundary?
- Are trust boundaries clear for user input, external API data, uploaded files, and AI output?
- Are secrets read from safe config rather than hardcoded?
- Are unsafe operations protected by explicit checks?

## Performance

- Are queries bounded and indexed where needed?
- Are N+1 calls avoided?
- Are frontend renders and effects stable?
- Are large payloads, streaming, caching, and pagination considered where relevant?

## Tests

- Is there at least one meaningful test or smoke path for changed behavior?
- Do tests cover failure or boundary cases when risk is non-trivial?
- Were generated snapshots or brittle tests avoided unless appropriate?
- Did the verification command actually run?

## AI/RAG/Agent Addendum

- Is retrieved context traceable to source?
- Does the model abstain when evidence is missing?
- Are tool errors detected and recovered from?
- Are prompt-injection boundaries explicit?
- Are cost, latency, retries, and timeouts controlled?
- Are eval cases included for normal, missing, conflicting, long-context, and adversarial inputs?

