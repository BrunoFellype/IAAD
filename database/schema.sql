DROP DATABASE IF EXISTS torneio_robotica;
CREATE DATABASE torneio_robotica;
USE torneio_robotica;

-- 1. Tabela Equipe
CREATE TABLE equipe (
    id_equipe INT AUTO_INCREMENT PRIMARY KEY,
    nome_equipe VARCHAR(100) NOT NULL,
    escola VARCHAR(100) NOT NULL,
    cidade VARCHAR(80) NOT NULL
);

-- 2. Tabela Membro da Equipe
CREATE TABLE membro_equipe (
    id_membro INT AUTO_INCREMENT PRIMARY KEY,
    nome_membro VARCHAR(100) NOT NULL,
    funcao VARCHAR(50),
    id_equipe INT NOT NULL,
    FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 3. Tabela Robo
CREATE TABLE robo (
    id_robo INT AUTO_INCREMENT PRIMARY KEY,
    nome_robo VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    data_criacao DATE NOT NULL,
    id_equipe INT NOT NULL,
    FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 4. Tabela Resultado
CREATE TABLE resultado (
    id_resultado INT AUTO_INCREMENT PRIMARY KEY,
    nome_prova VARCHAR(100) NOT NULL,
    classificacao INT DEFAULT 0,
    pontuacao DECIMAL(6,2) NOT NULL,
    id_robo INT NOT NULL,
    FOREIGN KEY (id_robo) REFERENCES robo(id_robo)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ==========================================================
-- TRIGGER: Validação de Pontuação e Ajuste Automático
-- ==========================================================
DELIMITER $$
CREATE TRIGGER trg_valida_pontuacao_insert
BEFORE INSERT ON resultado
FOR EACH ROW
BEGIN
    IF NEW.pontuacao < 0 THEN
        SET NEW.pontuacao = 0.00;
    ELSEIF NEW.pontuacao > 100.00 THEN
        SET NEW.pontuacao = 100.00;
    END IF;
END$$
DELIMITER ;

-- ==========================================================
-- TRIGGER: Validação de Compatibilidade entre Categoria e Prova
-- ==========================================================
DELIMITER $$
CREATE TRIGGER trg_valida_compatibilidade_prova
BEFORE INSERT ON resultado
FOR EACH ROW
BEGIN
    DECLARE v_categoria VARCHAR(50);
    
    SELECT categoria INTO v_categoria
    FROM robo
    WHERE id_robo = NEW.id_robo;
    
    IF v_categoria = 'Sumô de Robôs' AND NEW.nome_prova <> 'Duelo de Sumô' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro de Validação: Robôs da categoria "Sumô de Robôs" só podem participar da prova "Duelo de Sumô".';
        
    ELSEIF v_categoria = 'Combate 3kg' AND NEW.nome_prova <> 'Arena de Batalha' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro de Validação: Robôs da categoria "Combate 3kg" só podem participar da prova "Arena de Batalha".';
        
    ELSEIF v_categoria = 'Seguidor de Linha' AND NEW.nome_prova NOT IN ('Corrida de Velocidade', 'Circuito Urbano') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro de Validação: Robôs da categoria "Seguidor de Linha" só podem participar de "Corrida de Velocidade" ou "Circuito Urbano".';
    END IF;
END$$
DELIMITER ;

-- ==========================================================
-- STORED PROCEDURE: Aplicar Bônus por Categoria
-- ==========================================================
DELIMITER $$
CREATE PROCEDURE sp_aplicar_bonus_categoria(
    IN p_categoria VARCHAR(50),
    IN p_percentual DECIMAL(5,2)
)
BEGIN
    UPDATE resultado res
    JOIN robo r ON res.id_robo = r.id_robo
    SET res.pontuacao = LEAST(100.00, res.pontuacao + (res.pontuacao * (p_percentual / 100)))
    WHERE r.categoria = p_categoria;
END$$
DELIMITER ;

-- ==========================================================
-- STORED PROCEDURE: Inserção de Resultado com Ranking Automático
-- ==========================================================
DELIMITER $$
CREATE PROCEDURE sp_inserir_resultado(
    IN p_nome_prova VARCHAR(100),
    IN p_pontuacao DECIMAL(6,2),
    IN p_id_robo INT
)
BEGIN
    INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) 
    VALUES (p_nome_prova, 0, p_pontuacao, p_id_robo);
    
    SET @pos = 0;
    UPDATE resultado res
    JOIN (
        SELECT id_resultado, @pos := @pos + 1 AS nova_pos
        FROM resultado
        WHERE nome_prova = p_nome_prova
        ORDER BY pontuacao DESC, id_resultado ASC
    ) ranked ON res.id_resultado = ranked.id_resultado
    SET res.classificacao = ranked.nova_pos;
END$$
DELIMITER ;

-- ==========================================================
-- POPULANDO AS TABELAS (Dados Expandidos)
-- ==========================================================

-- 1. Equipes (Adicionadas mais 4 equipes, incluindo uma sem robôs)
INSERT INTO equipe (nome_equipe, escola, cidade) VALUES 
('CyberTech', 'Escola Técnica Estadual', 'Recife'),
('RoboMasters', 'IFPE Campus Recife', 'Recife'),
('Titanium', 'Colégio Dom Bosco', 'Olinda'),
('MechWarriors', 'UFRPE - Unidade Sede', 'Recife'),
('AlphaBot', 'Colégio Boa Viagem', 'Recife'),
('TecnoSpark', 'ETEP', 'Jaboatão dos Guararapes'),
('ThunderRobotics', 'SESI Pana', 'Paulista'),
('ByteForge', 'IFPB', 'João Pessoa'),
('Quantum', 'Escola Referência', 'Igarassu'); -- Mais uma equipe sem robô para testes

-- 2. Membros das Equipes (Adicionados mais membros distribuídos)
INSERT INTO membro_equipe (nome_membro, funcao, id_equipe) VALUES 
('Joana Silva', 'Programadora', 1),
('Carlos Souza', 'Construtor', 1),
('Mariana Lima', 'Pilota', 2),
('João Pedro', 'Estrategista', 3),
('Lucas Martins', 'Capitão', 4),
('Beatriz Alves', 'Designer', 5),
('Gabriel Santos', 'Programador', 5),
('Larissa Mendes', 'Pilota', 6),
('Mateus Rocha', 'Mecânico', 7),
('Camila Duarte', 'Estrategista', 8),
('Felipe Araujo', 'Programador', 2);

-- 3. Robôs (Adicionados mais robôs com suas respectivas categorias corretas)
INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe) VALUES 
('Optimus Jr', 'Seguidor de Linha', '2025-11-10', 1),
('Vortex', 'Sumô de Robôs', '2026-02-15', 2),
('Blitz', 'Combate 3kg', '2026-04-01', 3),
('Sentinel', 'Seguidor de Linha', '2026-06-20', 1),
('Goliath', 'Combate 3kg', '2026-01-10', 5),
('Tornado', 'Sumô de Robôs', '2026-03-12', 6),
('Flash', 'Seguidor de Linha', '2026-05-05', 7),
('Destructor', 'Combate 3kg', '2026-07-08', 8),
('Apex', 'Sumô de Robôs', '2026-08-19', 2),
('Striker', 'Seguidor de Linha', '2026-09-01', 7);

-- 4. Resultados (Adicionados mais resultados compatíveis com as regras das provas)
INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) VALUES 
('Corrida de Velocidade', 1, 95.50, 1),
('Duelo de Sumô', 1, 82.00, 2),
('Arena de Batalha', 1, 98.00, 3),
('Circuito Urbano', 1, 76.00, 4),
('Arena de Batalha', 2, 88.50, 5),
('Duelo de Sumô', 2, 79.00, 6),
('Corrida de Velocidade', 2, 91.20, 7),
('Arena de Batalha', 3, 65.00, 8),
('Duelo de Sumô', 3, 85.40, 9),
('Circuito Urbano', 2, 89.00, 10);