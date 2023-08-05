CREATE MIGRATION m1v52mzxwl4irugsh5lgi4rlb67rjpeew6sqajgugizkvla5k7hena
    ONTO m13z53y3jdctjyaq55oc6wjmqbnrev6l2ldwipv6qggbq63v7ll7bq
{
  ALTER TYPE default::Workflow {
      CREATE PROPERTY locations -> std::json;
  };
};
