CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE(name VARCHAR(100), phone VARCHAR(20)) AS $$
BEGIN
    RETURN QUERY
    SELECT p.name, p.phone
    FROM contacts c
    WHERE p.name ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION get_contacts_paginated(lim INT, off INT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM phonebook
    LIMIT lim OFFSET off;
END;
$$ LANGUAGE plpgsql;