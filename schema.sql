-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for Crops
CREATE TABLE IF NOT EXISTS crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    ph_min FLOAT NOT NULL,
    ph_max FLOAT NOT NULL,
    rain_min FLOAT NOT NULL, -- mm/year
    rain_max FLOAT NOT NULL,
    temp_min FLOAT NOT NULL, -- Celsius
    temp_max FLOAT NOT NULL,
    sun_requirement TEXT NOT NULL, -- 'Low', 'Medium', 'High'
    soil_type TEXT NOT NULL, -- 'Sandy', 'Clay', 'Loam', 'Silt'
    irrigation_need TEXT NOT NULL, -- 'Low', 'Medium', 'High'
    description TEXT
);

-- Table for User Inputs
CREATE TABLE IF NOT EXISTS user_inputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID DEFAULT uuid_generate_v4(), -- Anonymous user tracking
    ph_value FLOAT,
    rain_value FLOAT,
    temp_value FLOAT,
    sun_value FLOAT, -- Normalized 0-1 or specific scale
    irrigation_value FLOAT, -- Normalized 0-1
    soil_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed Data for Crops
INSERT INTO crops (name, ph_min, ph_max, rain_min, rain_max, temp_min, temp_max, sun_requirement, soil_type, irrigation_need, description)
VALUES
('Padi', 5.0, 7.0, 1500, 2500, 20, 35, 'High', 'Clay', 'High', 'Tanaman pangan utama, butuh banyak air.'),
('Jagung', 5.5, 7.5, 500, 1500, 18, 32, 'High', 'Loam', 'Medium', 'Tanaman palawija, toleran kekeringan sedang.'),
('Cabai', 5.5, 6.8, 600, 1200, 18, 30, 'High', 'Sandy Loam', 'Medium', 'Butuh drainase baik, tidak tahan genangan.'),
('Tomat', 6.0, 7.0, 600, 1500, 18, 27, 'High', 'Loam', 'Medium', 'Sensitif terhadap kelembaban tinggi.'),
('Bawang Merah', 6.0, 7.0, 350, 1000, 25, 32, 'High', 'Loam', 'Medium', 'Butuh cuaca cerah dan tanah gembur.'),
('Kentang', 5.0, 6.5, 1500, 2500, 15, 20, 'Medium', 'Loam', 'Medium', 'Tanaman dataran tinggi, suhu sejuk.'),
('Sawi', 6.0, 7.0, 1000, 2000, 20, 30, 'Medium', 'Loam', 'High', 'Sayuran daun, masa panen cepat.');
