CREATE MIGRATION m1upk3o32fzrzjhdw66lqssw6eh35vpm4qwmnprw4h2gxwophidf2q
    ONTO m1yi6ig242bvax5n7cvu4b2wqrqchthygwbldnlchhftgmms6tmcbq
{
  ALTER TYPE default::NodeInstance {
      DROP PROPERTY decision_options;
  };
};
