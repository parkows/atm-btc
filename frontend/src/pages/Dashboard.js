import React, { useEffect, useState } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Select, MenuItem, FormControl, InputLabel, Box, CircularProgress, Link as MuiLink } from '@mui/material';
import { Link } from 'react-router-dom';
import axios from 'axios';

const statusOptions = [
  { value: '', label: 'Todos' },
  { value: 'aguardando_invoice', label: 'Aguardando Invoice' },
  { value: 'aguardando_pagamento', label: 'Aguardando Pagamento' },
  { value: 'pago', label: 'Pago' },
  { value: 'expirada', label: 'Expirada' },
];

export default function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    axios.get(`/api/atm/sessions${status ? `?status=${status}` : ''}`)
      .then(res => setSessions(res.data))
      .finally(() => setLoading(false));
  }, [status]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard de Sessões</Typography>
      <FormControl sx={{ minWidth: 200, mb: 2 }}>
        <InputLabel>Status</InputLabel>
        <Select value={status} label="Status" onChange={e => setStatus(e.target.value)}>
          {statusOptions.map(opt => (
            <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
          ))}
        </Select>
      </FormControl>
      {loading ? <CircularProgress /> : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Código</TableCell>
                <TableCell>ATM</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Valor ARS</TableCell>
                <TableCell>BTC Esperado</TableCell>
                <TableCell>Invoice</TableCell>
                <TableCell>Invoice Status</TableCell>
                <TableCell>Criado em</TableCell>
                <TableCell>Detalhes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sessions.map(s => (
                <TableRow key={s.session_code}>
                  <TableCell>{s.session_code}</TableCell>
                  <TableCell>{s.atm_id}</TableCell>
                  <TableCell>{s.status}</TableCell>
                  <TableCell>{s.amount_ars?.toLocaleString('pt-BR', {minimumFractionDigits:2})}</TableCell>
                  <TableCell>{s.btc_expected?.toFixed(8)}</TableCell>
                  <TableCell sx={{ maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.invoice}</TableCell>
                  <TableCell>{s.invoice_status}</TableCell>
                  <TableCell>{new Date(s.created_at).toLocaleString('pt-BR')}</TableCell>
                  <TableCell><MuiLink component={Link} to={`/simular/${s.session_code}`}>Ver</MuiLink></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
} 