CREATE MIGRATION m1ap7iwlyvy3rb7bdq5sh4uxjd3cql3idvixckrlaqef26ohrb3neq
    ONTO m1e7k2ykkxnn5qblnawunytvjsuunr2skr4io3p7255433bi2ugoda
{
  CREATE TYPE default::Lane {
      CREATE REQUIRED PROPERTY system -> std::str;
      CREATE REQUIRED PROPERTY system_identifier -> std::str;
  };
  ALTER TYPE default::NodeInstance {
      CREATE MULTI LINK lanes -> default::Lane;
  };
  ALTER TYPE default::Lane {
      CREATE MULTI LINK usages := (.<lanes[IS default::NodeInstance]);
  };
};
