-------------------------------------------------------------
-- Material Types
-------------------------------------------------------------

CREATE TABLE material_type
(
    material_type_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            VARCHAR(30) NOT NULL,
    description     VARCHAR(200),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_material_type_code UNIQUE (code)
);

-------------------------------------------------------------
-- Production Methods
-------------------------------------------------------------

CREATE TABLE production_method
(
    production_method_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code                 VARCHAR(30) NOT NULL,
    description          VARCHAR(200),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_production_method_code UNIQUE (code)
);

-------------------------------------------------------------
-- Material Stock
-------------------------------------------------------------

CREATE TABLE material_stock
(
    material_stock_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    colour_name      VARCHAR(100) NOT NULL,

    material_type_id BIGINT NOT NULL,

    quantity_in_stock INTEGER NOT NULL DEFAULT 0,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,

    CONSTRAINT fk_material_stock_material_type
        FOREIGN KEY (material_type_id)
        REFERENCES material_type(material_type_id),

    CONSTRAINT chk_material_stock_quantity
        CHECK (quantity_in_stock >= 0)
);

CREATE INDEX ix_material_stock_material_type
ON material_stock(material_type_id);

-------------------------------------------------------------
-- Jobs
-------------------------------------------------------------

CREATE TABLE dice_job
(
    dice_job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_name VARCHAR(200) NOT NULL,

    description TEXT,

    job_date DATE NOT NULL,

    colour_count INTEGER NOT NULL,

    production_method_id BIGINT NOT NULL,

    primary_material_stock_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,

    CONSTRAINT fk_dice_job_method
        FOREIGN KEY (production_method_id)
        REFERENCES production_method(production_method_id),

    CONSTRAINT fk_dice_job_primary_material
        FOREIGN KEY (primary_material_stock_id)
        REFERENCES material_stock(material_stock_id),

    CONSTRAINT chk_colour_count
        CHECK (colour_count > 0)
);

CREATE INDEX ix_dice_job_method
ON dice_job(production_method_id);

CREATE INDEX ix_dice_job_material
ON dice_job(primary_material_stock_id);

-------------------------------------------------------------
-- Job Colours (Many Colours per Job)
-------------------------------------------------------------

CREATE TABLE dice_job_colour
(
    dice_job_colour_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dice_job_id BIGINT NOT NULL,

    material_stock_id BIGINT NOT NULL,

    colour_order SMALLINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_job_colour_job
        FOREIGN KEY (dice_job_id)
        REFERENCES dice_job(dice_job_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_job_colour_material
        FOREIGN KEY (material_stock_id)
        REFERENCES material_stock(material_stock_id),

    CONSTRAINT uq_job_colour
        UNIQUE (dice_job_id, material_stock_id)
);

CREATE INDEX ix_job_colour_job
ON dice_job_colour(dice_job_id);

CREATE INDEX ix_job_colour_material
ON dice_job_colour(material_stock_id);

-------------------------------------------------------------
-- Allowed Materials for a Production Method
-------------------------------------------------------------

CREATE TABLE production_method_material
(
    production_method_id BIGINT NOT NULL,

    material_type_id BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY
    (
        production_method_id,
        material_type_id
    ),

    CONSTRAINT fk_method_material_method
        FOREIGN KEY (production_method_id)
        REFERENCES production_method(production_method_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_method_material_type
        FOREIGN KEY (material_type_id)
        REFERENCES material_type(material_type_id)
        ON DELETE CASCADE
);

CREATE INDEX ix_method_material_type
ON production_method_material(material_type_id);