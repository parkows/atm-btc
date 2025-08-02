import React, { useState } from 'react';
import { Box, Typography, Button, Alert, Paper, InputAdornment, TextField } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { NumericFormat } from 'react-number-format';

export default function Simular() {
  const [atmId, setAtmId] = useState('ATM001');
  const [amount, setAmount] = useState('10000.00');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    // Corrigir conversão: NumericFormat envia .value como string sem formatação, mas fallback para parse correto
    let num = Number(amount);
    if (isNaN(num) || num < 10000 || num > 150000) {
      setError('O valor deve estar entre 10.000 e 150.000 ARS');
      setLoading(false);
      return;
    }
    try {
      const res = await axios.post('/api/atm/session', {
        atm_id: atmId,
        amount_ars: num
      });
      navigate(`/simular/${res.data.session_code}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar sessão');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box maxWidth={400} mx="auto" mt={4} component={Paper} p={3}>
      <Typography variant="h5" gutterBottom>Simular ATM - Criar Sessão</Typography>
      <form onSubmit={handleSubmit}>
        <TextField label="ATM ID" value={atmId} onChange={e => setAtmId(e.target.value)} fullWidth margin="normal" required />
        <NumericFormat
          customInput={TextField}
          label="Valor em ARS"
          value={amount}
          onValueChange={(values) => setAmount(values.value)}
          thousandSeparator="."
          decimalSeparator="," 
          decimalScale={2}
          fixedDecimalScale
          allowNegative={false}
          allowLeadingZeros={false}
          prefix="$ "
          fullWidth
          margin="normal"
          required
          InputProps={{
            startAdornment: <InputAdornment position="start">$</InputAdornment>,
          }}
          inputProps={{ inputMode: 'decimal' }}
          isAllowed={({ floatValue }) => (floatValue === undefined || (floatValue <= 150000 && floatValue >= 0))}
          helperText="Entre $ 10.000,00 e $ 150.000,00"
        />
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Button type="submit" variant="contained" color="primary" fullWidth disabled={loading} sx={{ mt: 2 }}>
          {loading ? 'Criando...' : 'Criar Sessão'}
        </Button>
      </form>
    </Box>
  );
} 