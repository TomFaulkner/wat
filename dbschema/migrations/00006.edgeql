CREATE MIGRATION m1lv4r7ilbhfynoymfdbkjzdvlv7dtuelcvfiy4l6hd5ysrbyyrdoa
    ONTO m1jlhfxyye7xkygz63dbkmljqtfzmazkiu7nf5z2wsh5io4qbbvrgq
{
  ALTER TYPE default::NodeInstance {
      DROP PROPERTY decision_options;
  };
};
