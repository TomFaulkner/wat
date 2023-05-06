CREATE MIGRATION m1yi6ig242bvax5n7cvu4b2wqrqchthygwbldnlchhftgmms6tmcbq
    ONTO m1pkgdfbsbfdgn4ef2xqhp7xbtnkkzl6ihjik5wr3uujopa6px7rxa
{
  ALTER TYPE default::NodeInstance {
      CREATE PROPERTY sequence -> std::int16;
  };
};
