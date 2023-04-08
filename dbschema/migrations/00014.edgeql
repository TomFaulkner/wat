CREATE MIGRATION m1r7s3liocopfcn3bzvntkyiqrkd3l7efzv6hqqy7zxezaapg4ezta
    ONTO m1z7qzw3mp7rrwomawqqcc4plelbpc5loxmmncfrazwmftl2qidomq
{
  ALTER TYPE default::StartRequirements {
      DROP LINK attribs;
  };
  ALTER TYPE default::Workflow {
      DROP LINK start_requirements;
  };
  DROP TYPE default::StartRequirements;
};
