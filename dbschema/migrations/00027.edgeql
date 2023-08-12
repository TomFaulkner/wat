CREATE MIGRATION m1xmkubihybcg6lkrvy3d674zbskyafscdaqtoshsvhhat3nlgdpjq
    ONTO m1ad33rmvbqa32gbdlkucebrlh66rduxzqzxgx4uy5w3ytvrepyyla
{
  ALTER TYPE default::NodeInstance {
      CREATE PROPERTY template -> std::bool;
      CREATE PROPERTY template_active -> std::bool;
  };
};
