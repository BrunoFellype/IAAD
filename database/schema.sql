CREATE DATABASE IF NOT EXISTS torneio_robotica;
USE torneio_robotica;

-- 1. Tabela Equipe
CREATE TABLE equipe (
    id_equipe INT AUTO_INCREMENT PRIMARY KEY,
    nome_equipe VARCHAR(100) NOT NULL,
    escola VARCHAR(100) NOT NULL,
    cidade VARCHAR(80) NOT NULL
);

-- 2. Tabela Nova_Tabela (Escolha livre: Membros da Equipe)
CREATE TABLE membro_equipe (
    id_membro INT AUTO_INCREMENT PRIMARY KEY,
    nome_membro VARCHAR(100) NOT NULL,
    funcao VARCHAR(50), -- Ex: Programador, Builder, Piloto
    id_equipe INT,
    FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe) ON DELETE CASCADE
);

-- 3. Tabela Robo
CREATE TABLE robo (
    id_robo INT AUTO_INCREMENT PRIMARY KEY,
    nome_robo VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    data_criacao DATE NOT NULL,
    id_equipe INT,
    FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe) ON DELETE CASCADE
);

-- 4. Tabela Resultado
CREATE TABLE resultado (
    id_resultado INT AUTO_INCREMENT PRIMARY KEY, -- Chave primária recomendada
    nome_prova VARCHAR(100) NOT NULL,
    classificacao INT NOT NULL,
    pontuacao DECIMAL(6,2) NOT NULL,
    id_robo INT,
    FOREIGN KEY (id_robo) REFERENCES robo(id_robo) ON DELETE CASCADE
);

-- Inserindo dados de exemplo para testes
INSERT INTO equipe (nome_equipe, escola, cidade) VALUES 
('CyberTech', 'Escola Estadual Central', 'Recife'),
('RoboMasters', 'IFPE Campus Recife', 'Recife'),
('Titanium', 'Colégio Dom Bosco', 'Olinda');

INSERT INTO membro_equipe (nome_membro, funcao, id_equipe) VALUES 
('Ana Silva', 'Programadora', 1),
('Carlos Souza', 'Construtor', 1),
('Mariana Lima', 'Pilota', 2),
('João Pedro', 'Estrategista', 3);

INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe) VALUES 
('Optimus Jr', 'Seguidor de Linha', '2026-03-10', 1),
('Vortex', 'Sumô de Robôs', '2026-04-15', 2),
('Blitz', 'Combate 3kg', '2026-05-01', 3);

INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) VALUES 
('Corrida de Velocidade', 1, 98.50, 1),
('Duelo de Sumô', 2, 85.00, 2),
('Arena de Batalha', 1, 100.00, 3);