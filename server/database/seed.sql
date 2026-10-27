INSERT INTO rooms (name, display_name) VALUES
    ('kitchen', 'Küche'),
    ('bath',    'Bad'),
    ('living',  'Wohnzimmer')
ON CONFLICT (name) DO UPDATE SET display_name = EXCLUDED.display_name;

INSERT INTO esp_nodes (name, room_name) VALUES
    ('esp-e868e71c3594mp', 'kitchen'),
    ('esp-a4f00f76b958', 'bed_room'),
    ('esp-206ef1fffe15'), 'living_room')
ON CONFLICT (name) DO UPDATE SET room_name = EXCLUDED.room_name;