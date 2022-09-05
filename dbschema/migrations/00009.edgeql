CREATE MIGRATION m1ooky7cxdl4en25ijtmvsvti7b32novtbgq4wx6bfieshmu3adqca
    ONTO m1dxjyhrzwtfzds7wt7mobywtt2f4y6fifv2oheoixqmks6dl56eva
{
  ALTER TYPE default::NodeInstance {
      CREATE PROPERTY decision_options -> array<std::uuid>;
  };
};
