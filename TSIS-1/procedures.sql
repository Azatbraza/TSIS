CREATE OR REPLACE PROCEDURE upsert_user(p_name TEXT, p_phone TEXT) AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO phonebook(name, phone) VALUES (p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE insert_many(names TEXT[], phones TEXT[]) AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(names, 1) LOOP
        IF phones[i] ~ '^[0-9]+$' THEN
            INSERT INTO phonebook(name, phone) VALUES (names[i], phones[i]);
        ELSE
            RAISE NOTICE 'Invalid phone: %', phones[i];
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_user(value TEXT) AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = value OR phone = value;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
AS $$
DECLARE
    c_id INT;
BEGIN
    SELECT id INTO c_id
    FROM contacts
    WHERE name = p_contact_name;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (c_id, p_phone, p_type);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
AS $$
DECLARE
    g_id INT;
BEGIN
    SELECT id INTO g_id
    FROM groups
    WHERE name = p_group_name;

    IF g_id IS NULL THEN
        INSERT INTO groups(name)
        VALUES(p_group_name)
        RETURNING id INTO g_id;
    END IF;

    UPDATE contacts
    SET group_id = g_id
    WHERE name = p_contact_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    name VARCHAR,
    email VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.email, p.phone
    FROM contacts c
    JOIN phones p ON c.id = p.contact_id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR p.phone ILIKE '%' || p_query || '%';
END;
$$ LANGUAGE plpgsql;