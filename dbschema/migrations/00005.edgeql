CREATE MIGRATION m1jlhfxyye7xkygz63dbkmljqtfzmazkiu7nf5z2wsh5io4qbbvrgq
    ONTO m1g3ot7zryb6or7fo4oxijvo7ppgensrw4tl5fzomzn65siyxhmora
{
  ALTER TYPE default::NodeInstance {
      CREATE PROPERTY decision_options -> array<std::uuid>;
  };
};
