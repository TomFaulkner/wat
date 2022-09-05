CREATE MIGRATION m1dxjyhrzwtfzds7wt7mobywtt2f4y6fifv2oheoixqmks6dl56eva
    ONTO m1udd27ijgpyt5ej5lp33f3jolv2bbec3f5l2jzosetwlnwmxeflna
{
  ALTER TYPE default::NodeInstance {
      DROP LINK decision_options;
  };
};
