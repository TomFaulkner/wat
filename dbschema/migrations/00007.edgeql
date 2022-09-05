CREATE MIGRATION m1udd27ijgpyt5ej5lp33f3jolv2bbec3f5l2jzosetwlnwmxeflna
    ONTO m1lv4r7ilbhfynoymfdbkjzdvlv7dtuelcvfiy4l6hd5ysrbyyrdoa
{
  ALTER TYPE default::NodeInstance {
      CREATE MULTI LINK decision_options -> default::NodeInstance;
  };
};
