CREATE MIGRATION m1cgsg4nvb5i3v6qis5l5uawov3u2ubrgj35fzx3kfeapu6gbxybhq
    ONTO m1dadgyzisariiooqirsuhze46qk5bwypsfy6knwbxn4j44evmvd5a
{
  CREATE TYPE default::StateAttributes {
      CREATE REQUIRED PROPERTY attribute_name -> std::str;
      CREATE REQUIRED PROPERTY attribute_type -> std::str;
      CREATE PROPERTY default_value -> std::str;
  };
  CREATE TYPE default::StartRequirements {
      CREATE REQUIRED MULTI LINK attribs -> default::StateAttributes;
  };
  ALTER TYPE default::Workflow {
      CREATE LINK start_requirements -> default::StartRequirements;
  };
};
