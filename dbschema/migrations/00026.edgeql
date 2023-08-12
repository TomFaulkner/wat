CREATE MIGRATION m1ad33rmvbqa32gbdlkucebrlh66rduxzqzxgx4uy5w3ytvrepyyla
    ONTO m1v52mzxwl4irugsh5lgi4rlb67rjpeew6sqajgugizkvla5k7hena
{
  ALTER TYPE default::Workflow {
      CREATE LINK ingestion := (.<workflow[IS default::IngestionRegistry]);
  };
};
