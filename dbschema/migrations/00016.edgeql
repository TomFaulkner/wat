CREATE MIGRATION m1aip53kukpztu7xxkpydz7u65seew26zvkcbcymwcltxd4vvcjyfq
    ONTO m1xhqoqtepy4f3f3yefoilzimutwnueynyz6rtf42ok7hdchtow6la
{
  ALTER TYPE default::Workflow {
      CREATE PROPERTY name -> std::str;
      CREATE PROPERTY version -> std::int16;
  };
};
