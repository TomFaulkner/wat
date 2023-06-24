select Lane {
  system, system_identifier, key :{ key }
}
filter .system = <str>$system and .system_identifier = <str>$system_identifier;
