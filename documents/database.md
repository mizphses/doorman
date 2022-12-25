
```sql
-- timestamp
CREATE FUNCTION refresh_updated_at_1() RETURNS trigger AS
$$
BEGIN
  IF NEW.updated_at = OLD.updated_at THEN
    NEW.updated_at := NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION refresh_updated_at_2() RETURNS trigger AS
$$
BEGIN
  IF NEW.updated_at IS NULL THEN
    NEW.updated_at := OLD.updated_at;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION refresh_updated_at_3() RETURNS trigger AS
$$
BEGIN
  IF NEW.updated_at IS NULL THEN
    NEW.updated_at := CURRENT_TIMESTAMP;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- reservations
CREATE TABLE if not exists reservations(
  id SERIAL,
  roomid VARCHAR NOT NULL,
  userid VARCHAR NOT NULL,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  type_of_usage VARCHAR NOT NULL,
  allowed_users VARCHAR NOT NULL DEFAULT false,
  note VARCHAR NOT NULL,
  approval BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER refresh_reservations_updated_at_1
  BEFORE UPDATE ON reservations FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_1();
CREATE TRIGGER refresh_reservations_updated_at_2
  BEFORE UPDATE OF updated_at ON reservations FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_2();
CREATE TRIGGER refresh_reservations_updated_at_3
  BEFORE UPDATE ON reservations FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_3();

```