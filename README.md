
# Shhh!

## Structured HTTP Headers (handily)

This is a [Python 3](https://python.org/) library implementing parsing and serialisation of [Structured Headers for HTTP](https://httpwg.org/http-extensions/draft-ietf-httpbis-header-structure.html).

Shhh's initial purpose is to prove the algorithms in the specification; as a result, it is not at all optimised. It tracks the specification closely, but since it is not yet an RFC, may change at any time.

The top-level `parse` and `serialise` functions are the ones your code should call.
