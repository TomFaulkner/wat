CREATE MIGRATION m1dadgyzisariiooqirsuhze46qk5bwypsfy6knwbxn4j44evmvd5a
    ONTO m1ooky7cxdl4en25ijtmvsvti7b32novtbgq4wx6bfieshmu3adqca
{
  ALTER TYPE default::NodeInstance {
      CREATE PROPERTY required_state -> array<std::str>;
  };
};
