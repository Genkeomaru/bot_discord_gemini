-- Criação da tabela de usuários do bot Discord
CREATE TABLE IF NOT EXISTS usuarios (
    id            TEXT PRIMARY KEY,
    username      TEXT NOT NULL,
    servidor_id   TEXT,
    registrado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ia_preferida  TEXT DEFAULT 'gemini',
    ativo         BOOLEAN DEFAULT TRUE
);

-- Índice para consultas por servidor
CREATE INDEX IF NOT EXISTS idx_usuarios_servidor_id ON usuarios (servidor_id);

-- Habilita Row Level Security
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Policy: service role tem acesso total (usado pelo supabase-py no backend)
CREATE POLICY "service_role_all"
    ON usuarios
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
