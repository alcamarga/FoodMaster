CREATE TYPE sizeenum AS ENUM ('Pequeña','Mediana','Familiar');

ALTER TABLE receta_item
ADD COLUMN size sizeenum NOT NULL DEFAULT 'Pequeña';
