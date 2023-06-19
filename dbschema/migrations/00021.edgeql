CREATE MIGRATION m1e7k2ykkxnn5qblnawunytvjsuunr2skr4io3p7255433bi2ugoda
    ONTO m123367tlz7hg3wfnv2fo74cocfft6tpvkjo3gng5shtdsx57z7sia
{
  ALTER TYPE default::Node {
      ALTER PROPERTY base {
          CREATE CONSTRAINT std::one_of('start', 'finish', 'decision', 'action', 'interactive');
      };
  };
  ALTER TYPE default::Node {
      ALTER PROPERTY base {
          DROP CONSTRAINT std::one_of('start', 'finish', 'decision', 'action');
      };
  };
};
