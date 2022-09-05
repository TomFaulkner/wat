CREATE MIGRATION m1g3ot7zryb6or7fo4oxijvo7ppgensrw4tl5fzomzn65siyxhmora
    ONTO m1txlpziol34styswh5pvxrwnhmxanevmgosaiz3if4k5ss7yyyjaa
{
  ALTER TYPE default::NodeInstance {
      ALTER PROPERTY state {
          CREATE CONSTRAINT std::one_of('started', 'cancelled', 'completed', 'error', 'waiting', 'blocked');
      };
  };
  ALTER TYPE default::NodeInstance {
      ALTER PROPERTY state {
          DROP CONSTRAINT std::one_of('started', 'cancelled', 'completed', 'error', 'waiting');
      };
  };
};
