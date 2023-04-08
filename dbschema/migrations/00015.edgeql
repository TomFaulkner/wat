CREATE MIGRATION m1xhqoqtepy4f3f3yefoilzimutwnueynyz6rtf42ok7hdchtow6la
    ONTO m1r7s3liocopfcn3bzvntkyiqrkd3l7efzv6hqqy7zxezaapg4ezta
{
  ALTER TYPE default::Workflow {
      CREATE MULTI LINK start_requirements -> default::StateAttributes;
  };
};
