# Overview

This section provides examples of how to use this OTEAPI plugin to perform OPTIMADE queries and handle the results.

In [Use OTEAPI-OPTIMADE with OTElib](otelib) you can find an example of how to use this plugin with the [OTElib](https://github.com/EMMC-ASBL/otelib) client.

It is worth noting that there are several different ways to use the strategies in this plugin.
For example, an OPTIMADE query can be provided using the `OPTIMADE` filter strategy, but it can also be provided directly in the URL value of the `OPTIMADE` data resource strategy's `accessUlr` parameter.
Further, it could be set through a `configuration` parameter entry to either of these strategies.

In the examples only one of these options are given, and this is the same for other aspects: What we believe is the most common and transparent use case is given.

Finally, it is important to note that using OTElib directly is not intended for end users.
Using OTElib should be done as a backend task in a web application, and the results should be presented to the end user in a more user friendly way.
