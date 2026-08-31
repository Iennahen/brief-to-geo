# Payment orchestration vs payment gateway

**BLOCKED**

## Blocking

- C5 unsupported (comparative): Where a gateway only provides a means of access to payment processing, orchestration adds the ability to route, retry and reconcile transactions centrally across those providers.
- C10 unsupported (advisory): Test it against your own transaction data before using it in a business case.
- C14 unsupported (advisory): You may not need orchestration if your payment volume falls below the point where the added routing and reconciliation work pays off.
- C16 unsupported (advisory): Below that volume, or if you operate in a single market, adding a layer on top of your existing gateway may not be worth it.

## For review

- C9 partially supported: Treat the figure as a vendor estimate rather than a verified benchmark.

## Claims

| id | type | verdict | source | claim |
|---|---|---|---|---|
| C1 | definitional | supported | S1 | A payment gateway handles payment card transactions on a merchant's behalf. |
| C2 | definitional | supported | S1 | In standard industry definitions, a payment gateway is essentially another na... |
| C3 | definitional | supported | S1 | A payment gateway is distinct from an acquirer, which is the financial instit... |
| C4 | definitional | supported | S2 | An orchestration layer sits above one or more gateways and integrates multipl... |
| C5 | comparative | unsupported | S2 | Where a gateway only provides a means of access to payment processing, orches... |
| C6 | advisory | supported | S2 | Orchestration lets you manage several payment paths from one system instead o... |
| C7 | attributive | supported | S3 | Solidgate states that orchestration can lift approval rates by 10-30% using t... |
| C8 | attributive | supported | S3 | Solidgate does not publish the methodology, sample size or measurement period... |
| C9 | advisory | partial | S3 | Treat the figure as a vendor estimate rather than a verified benchmark. |
| C10 | advisory | unsupported | — | Test it against your own transaction data before using it in a business case. |
| C11 | definitional | supported | S4 | Authorisation rate is the percentage of card authorisation requests approved ... |
| C12 | definitional | supported | S4 | Approval rate also counts transactions recovered through retries, failover or... |
| C13 | comparative | supported | S4 | Approval rate is always equal to or higher than the first-attempt authorisati... |
| C14 | advisory | unsupported | S3 | You may not need orchestration if your payment volume falls below the point w... |
| C15 | attributive | supported | S3 | Solidgate states that orchestration pays for itself above roughly $400,000 pr... |
| C16 | advisory | unsupported | S3 | Below that volume, or if you operate in a single market, adding a layer on to... |

## Counts

- partial: 1
- supported: 11
- unsupported: 4
