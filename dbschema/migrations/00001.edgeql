CREATE MIGRATION m1u73dwuq2mxjggjxgcyhfjccupcxkzn27k3g4ai43ib6taqy7hkeq
    ONTO initial
{
  CREATE TYPE default::FlowState {
      CREATE PROPERTY created -> std::datetime;
      CREATE PROPERTY last_updated -> std::datetime;
      CREATE REQUIRED PROPERTY state -> std::json;
  };
  CREATE TYPE default::NodeType {
      CREATE REQUIRED PROPERTY base -> std::str {
          CREATE CONSTRAINT std::one_of('start', 'finish', 'decision', 'action');
      };
      CREATE PROPERTY type -> std::str {
          CREATE CONSTRAINT std::one_of('flow', 'api', 'ingestion', 'response', 'cron');
      };
  };
  CREATE TYPE default::Node {
      CREATE REQUIRED LINK base -> default::NodeType;
      CREATE REQUIRED PROPERTY config -> std::json;
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE REQUIRED PROPERTY template -> std::bool;
      CREATE REQUIRED PROPERTY version -> std::int16;
  };
  CREATE TYPE default::Workflow {
      CREATE LINK flowstate -> default::FlowState;
      CREATE REQUIRED PROPERTY state -> std::str {
          CREATE CONSTRAINT std::one_of('started', 'cancelled', 'completed', 'error', 'waiting', 'template');
      };
      CREATE PROPERTY template -> std::bool;
      CREATE PROPERTY template_active -> std::bool;
  };
  CREATE TYPE default::IngestionRegistry {
      CREATE REQUIRED LINK workflow -> default::Workflow;
      CREATE REQUIRED PROPERTY active -> std::bool;
      CREATE REQUIRED PROPERTY friendly_name -> std::str;
  };
  CREATE TYPE default::NodeInstance {
      CREATE REQUIRED LINK node -> default::Node;
      CREATE MULTI LINK parents -> default::NodeInstance;
      CREATE MULTI LINK children := (.<parents[IS default::NodeInstance]);
      CREATE MULTI LINK depends_on -> default::NodeInstance;
      CREATE REQUIRED LINK workflow -> default::Workflow;
      CREATE REQUIRED PROPERTY depends -> std::int16;
      CREATE REQUIRED PROPERTY state -> std::str {
          CREATE CONSTRAINT std::one_of('started', 'cancelled', 'completed', 'error', 'waiting');
      };
  };
  ALTER TYPE default::Workflow {
      CREATE MULTI LINK node_instances := (.<workflow[IS default::NodeInstance]);
  };
};
