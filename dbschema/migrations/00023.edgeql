CREATE MIGRATION m1u6seomlrzi62lpsexnzk3swymapqtx2ktomwm3xlwt45fqqsxv4a
    ONTO m1ap7iwlyvy3rb7bdq5sh4uxjd3cql3idvixckrlaqef26ohrb3neq
{
  ALTER TYPE default::Lane {
      DROP LINK usages;
      DROP PROPERTY system;
      DROP PROPERTY system_identifier;
  };
  ALTER TYPE default::NodeInstance {
      DROP LINK lanes;
  };
  DROP TYPE default::Lane;
};
