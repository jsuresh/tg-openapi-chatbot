-- Active bots, id is the telegram api key for the bot
CREATE TABLE IF NOT EXISTS bot (
  id VARCHAR NOT NULL,
  data text, -- app controlled blob (arbitrary json)
  PRIMARY KEY (id)
);

-- every chat session, id is the telegram chat session
CREATE TABLE IF NOT EXISTS chat (
  id VARCHAR NOT NULL,
  data text, -- app controlled blob (arbitrary json)
  PRIMARY KEY (id)
);