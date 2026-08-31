## Payment orchestration vs payment gateway — frequently asked questions

### What does a payment gateway do?

A payment gateway handles your card transactions for you. It's essentially another name for a payment processor or payment service provider. It's distinct from an acquirer, which is the financial institution that processes card transactions for merchants and is formally defined as such by a payment brand.

*Sources: S1*

### What does a payment orchestration layer add on top of a gateway?

An orchestration layer integrates multiple payment service providers, gateways and payment methods into a single platform. A gateway provides a means of access to payment processing; it is not a system for tailoring or optimising payment flows. Solidgate, a payments vendor, describes orchestration as routing, retrying and reconciling transactions centrally across multiple providers.

*Sources: S2, S3*

### How much do approval rates improve after adding orchestration?

Solidgate states that orchestration can lift approval rates by 10-30% using the same providers you already have. They don't share the methodology, sample size or measurement period behind that range, so keep in mind that it's a vendor's estimate rather than a measured benchmark.

*Sources: S3*

### What is the difference between authorisation rate and approval rate?

Authorisation rate is the percentage of card authorisation requests approved by the issuing bank, calculated as approved authorisations divided by total authorisation attempts. Approval rate is broader: it also counts transactions recovered through retries, failover or alternative payment methods after an initial decline. Because of that, approval rate is always equal to or higher than the first-attempt authorisation rate.

*Sources: S4*

### When does a merchant not need orchestration?

> **Not published.** I simply couldn't answer this from the evidence pack. The only related figure is Solidgate's $400,000 monthly threshold, which says when orchestration pays off, not when it doesn't. To answer it properly I'd need a source about smaller or single-market merchants, and until I have one, I'd rather skip than lie.

