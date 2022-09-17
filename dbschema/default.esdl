module default {
    type Node {
        required property name -> str;
        required property version -> int16;
        required property template -> bool;

        required property base -> str {
            constraint one_of (
                'start', 'finish',
                'decision', 'action'
            )
        };
        property type -> str {
            constraint one_of (
                'flow', 'api', 'ingestion', 'response', 'cron'
                # flow nodes are start/finish nodes that don't do anything
                # api nodes call apis
                # ingestion nodes wait for incoming requests and turn data to variables, configured using a simple, perhaps dot notation, syntax
                # ingestion could be a start node, but also not start if mid workflow?
                # response nodes return some sort of response to a requester (as a reply to an ingestion or start API request)
                # cron nodes, if active, wait until X time has passed or until Y time of day/week/month/etc.
            )
        }

        required property config -> json;
    }

    type NodeInstance {
        required link node -> Node;
        required property state -> str {
            constraint one_of (
                'started', 'cancelled', 'completed',
                'error', 'waiting', 'blocked'
            )
        };
        multi link parents -> NodeInstance;
        multi link children := .<parents[is NodeInstance];

        property decision_options -> array<uuid>;
        property required_state -> array<str>;

        # will wait for this number of parents in addition to depends_on
        # -1 all parents, 0 no parents, otherwise based on count
        required property depends -> int16;
        # which nodes does this node depend on
        multi link depends_on -> NodeInstance;

        required link workflow -> Workflow;
    }

# when a decision is made decision nodeinstance should find its children and cancel those not decided

    type Workflow {
        property template -> bool;
        property template_active -> bool;
        required property state -> str {
            constraint one_of (
                'started', 'cancelled', 'completed',
                'error', 'waiting', 'template'
            )
        }
        link flowstate -> FlowState;
        multi link node_instances := .<workflow[is NodeInstance];
    }

    type FlowState {
        required property state -> json;
        property created -> datetime;
        property last_updated -> datetime;
    }

    type IngestionRegistry {
         required property friendly_name -> str;
         required link workflow -> Workflow;
         required property active -> bool;
    }
}
