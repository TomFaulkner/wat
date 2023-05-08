CREATE MIGRATION m123367tlz7hg3wfnv2fo74cocfft6tpvkjo3gng5shtdsx57z7sia
    ONTO m1upk3o32fzrzjhdw66lqssw6eh35vpm4qwmnprw4h2gxwophidf2q
{
  ALTER TYPE default::NodeInstance {
      ALTER PROPERTY state {
          DROP CONSTRAINT std::one_of('started', 'cancelled', 'completed', 'error', 'waiting', 'blocked');
      };
  };
  ALTER TYPE default::NodeInstance {
      ALTER PROPERTY state {
          CREATE CONSTRAINT std::one_of('started', 'cancelled', 'completed', 'error', 'waiting', 'blocked', 'polling', 'pending');
      };
  };
};
