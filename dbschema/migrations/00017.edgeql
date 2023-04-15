CREATE MIGRATION m1pkgdfbsbfdgn4ef2xqhp7xbtnkkzl6ihjik5wr3uujopa6px7rxa
    ONTO m1aip53kukpztu7xxkpydz7u65seew26zvkcbcymwcltxd4vvcjyfq
{
  ALTER TYPE default::NodeInstance {
      CREATE PROPERTY config -> std::json;
  };
};
