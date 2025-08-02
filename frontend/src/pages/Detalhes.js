import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, Button, Alert, Chip, Stack, Tooltip, IconButton } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import axios from 'axios';

export default function Detalhes() {
  const { session_code } = useParams();
  const [session, setSession] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const navigate = useNavigate();

  const fetchSession = useCallback(() => {
    axios.get(`/api/atm/session/${session_code}`)
      .then(res => setSession(res.data))
      .catch(() => setError('Sessão não encontrada.'));
  }, [session_code]);

  useEffect(() => { fetchSession(); }, [fetchSession]);

  const handleCopy = () => {
    navigator.clipboard.writeText('redatm@strike.me');
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (!session) return <Typography>Carregando...</Typography>;

  return (
    <Box maxWidth={600} mx="auto" mt={4} component={Paper} p={3}>
      <Typography variant="h5" gutterBottom>Detalhes da Sessão</Typography>
      <Stack direction="row" spacing={1} mb={2}>
        <Chip label={session.status} color={session.status === 'pago' ? 'success' : session.status === 'expirada' ? 'error' : 'warning'} />
        <Chip label={session.invoice_status || ''} color={session.invoice_status === 'pago' ? 'success' : session.invoice_status === 'expirado' ? 'error' : 'warning'} />
      </Stack>
      <ul>
        <li><b>Código:</b> {session_code}</li>
        <li><b>ATM:</b> {session.atm_id}</li>
        <li><b>Valor ARS:</b> {session.amount_ars?.toLocaleString('pt-BR', {minimumFractionDigits:2})}</li>
        <li><b>BTC Esperado:</b> {session.btc_expected?.toFixed(8)}</li>
        <li><b>LN Address para pagamento:</b> <b>redatm@strike.me</b> <Tooltip title={copied ? 'Copiado!' : 'Copiar'}><IconButton size="small" onClick={handleCopy}><ContentCopyIcon fontSize="small" /></IconButton></Tooltip></li>
        <li><b>Status:</b> {session.status}</li>
        <li><b>Invoice Status:</b> {session.invoice_status || '-'}</li>
      </ul>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Button variant="outlined" onClick={() => navigate(-1)}>Voltar</Button>
    </Box>
  );
} 