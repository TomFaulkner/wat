CREATE MIGRATION m13z53y3jdctjyaq55oc6wjmqbnrev6l2ldwipv6qggbq63v7ll7bq
    ONTO m1u6seomlrzi62lpsexnzk3swymapqtx2ktomwm3xlwt45fqqsxv4a
{
  CREATE TYPE default::Keys {
      CREATE REQUIRED PROPERTY key -> std::str;
      CREATE REQUIRED PROPERTY last_modified -> std::datetime;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::Lane {
      CREATE REQUIRED LINK key -> default::Keys;
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
