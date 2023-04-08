CREATE MIGRATION m1z7qzw3mp7rrwomawqqcc4plelbpc5loxmmncfrazwmftl2qidomq
    ONTO m1tuncwl223tduj7sve3fu4wu3wwytkljg5alylrycwdoc5smsiprq
{
  ALTER TYPE default::StateAttributes {
      CREATE PROPERTY active -> std::bool {
          SET default := true;
      };
  };
};
