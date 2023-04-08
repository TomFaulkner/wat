CREATE MIGRATION m1tuncwl223tduj7sve3fu4wu3wwytkljg5alylrycwdoc5smsiprq
    ONTO m1cgsg4nvb5i3v6qis5l5uawov3u2ubrgj35fzx3kfeapu6gbxybhq
{
  ALTER TYPE default::StateAttributes {
      ALTER PROPERTY attribute_name {
          RENAME TO name;
      };
  };
  ALTER TYPE default::StateAttributes {
      ALTER PROPERTY attribute_type {
          RENAME TO type;
      };
  };
};
