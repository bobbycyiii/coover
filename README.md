# coover
Glue code between John Berge's program 
[`heegaard`](https://www.math.uic.edu/t3m) and Mark Bell,
Tracy Hall, and Saul Schleimer's program
[`twister`](https://bitbucket.org/Mark_Bell/twister), in two
parts: digestion and extraction. 

This completes the first implementation
of a solution to the following problem: given a realizable finite
presentation *P* of a group *G*, to construct a (possibly ideal) 3-manifold
triangulation with fundamental group *G*.

## Digestion
Using a series of regular expressions, digestion
converts the output of a `heegaard` session into
a format acceptable to [`Python`](https://www.python.org/)
(of which `twister` is a module).

Digestion is very sensitive to the particular form of
`heegaard`'s output. As such, digestion is very fragile and
should be made unnecessary as soon as possible. This could be
achieved by a standard format of output from `heegaard`; 
designing the format of the results of the above digestion 
process was a step in this direction.

## Extraction
This takes digested output from `heegaard` as input and
produces as output an associated `twister` surface file.

More specifically, the output from `heegaard` represents
a 3-manifold *M* by a spine *X* originating from a Heegaard
splitting along a surface *S* and its Whitehead graph. 
Extraction recovers from *X* a cubulation *K* of *S* and
two disjoint sets *D*, *H* of disjoint "hyperplanes" 
(i.e. *K*-normal curves which cut no corners) such that
attaching 2-handles to one side of *S x I* along *D* yields
a |*D*|-punctured genus-|*D*| handlebody, and such that
attaching discs along *D* on one side of *S* and along
*H* on the other side yields a 2-complex homotopy equivalent
to *X*, namely the Heegaard-splitting complex. (*X* is 
homotopy-equivalent to the Heegaard-splitting complex
by the contractibility of the cores and co-cores of the
handles in the handlebody.)

A less opaque explanation is upcoming work.
