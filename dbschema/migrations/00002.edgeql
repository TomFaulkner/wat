CREATE MIGRATION m1iay5sj5vfojva2xgaemrtn6h44xo6k2duvcgm2id5ysewhnuxynq
    ONTO m1u73dwuq2mxjggjxgcyhfjccupcxkzn27k3g4ai43ib6taqy7hkeq
{
  ALTER TYPE default::Node {
      DROP LINK base;
  };
};
