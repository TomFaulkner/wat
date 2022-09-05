CREATE MIGRATION m1txlpziol34styswh5pvxrwnhmxanevmgosaiz3if4k5ss7yyyjaa
    ONTO m1iay5sj5vfojva2xgaemrtn6h44xo6k2duvcgm2id5ysewhnuxynq
{
  ALTER TYPE default::Node {
      CREATE REQUIRED PROPERTY base -> std::str {
          SET REQUIRED USING ('start');
          CREATE CONSTRAINT std::one_of('start', 'finish', 'decision', 'action');
      };
      CREATE PROPERTY type -> std::str {
          CREATE CONSTRAINT std::one_of('flow', 'api', 'ingestion', 'response', 'cron');
      };
  };
  DROP TYPE default::NodeType;
};
