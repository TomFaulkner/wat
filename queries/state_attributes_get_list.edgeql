select StateAttributes
  filter .id in std::array_unpack(<array<uuid>>$start_requirements)
