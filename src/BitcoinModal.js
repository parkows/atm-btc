import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  CurrencyBitcoin as BitcoinIcon,
  QrCode as QrCodeIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

const steps = ['Informar Valor', 'Gerar Invoice', 'Aguardar Pagamento', 'Confirmar'];

function BitcoinModal({ open, onClose }) {
  const [activeStep, setActiveStep] = useState(0);
  const [amount, setAmount] = useState('');
  const [sessionCode, setSessionCode] = useState('');
  const [invoice, setInvoice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleNext = () => {
    if (activeStep === 0) {
      if (!amount || amount < 10000 || amount > 150000) {
        setError('Valor deve estar entre 10.000 e 150.000 ARS');
        return;
      }
      setError('');
      setLoading(true);
      // Simular criação de sessão
      setTimeout(() => {
        setSessionCode('123-456');
        setLoading(false);
        setActiveStep(1);
      }, 2000);
    } else if (activeStep === 1) {
      setLoading(true);
      // Simular geração de invoice
      setTimeout(() => {
        setInvoice('lnbc1testinvoice7');
        setLoading(false);
        setActiveStep(2);
      }, 2000);
    } else if (activeStep === 2) {
      setLoading(true);
      // Simular verificação de pagamento
      setTimeout(() => {
        setLoading(false);
        setActiveStep(3);
      }, 3000);
    } else {
      onClose();
      setActiveStep(0);
      setAmount('');
      setSessionCode('');
      setInvoice('');
      setError('');
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Informe o valor em ARS que deseja vender em Bitcoin
            </Typography>
            <TextField
              fullWidth
              label="Valor em ARS"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              sx={{ mt: 2 }}
              InputProps={{
                startAdornment: '$ ',
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
              Valor mínimo: $10.000 ARS | Valor máximo: $150.000 ARS
            </Typography>
          </Box>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Sessão criada com sucesso!
            </Typography>
            <Card sx={{ mt: 2, backgroundColor: '#f5f5f5' }}>
              <CardContent>
                <Typography variant="body1">
                  <strong>Código da Sessão:</strong> {sessionCode}
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  <strong>Valor:</strong> ${parseInt(amount).toLocaleString('pt-BR')} ARS
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  <strong>BTC Esperado:</strong> {(parseInt(amount) * 0.9 / 50000).toFixed(8)} BTC
                </Typography>
              </CardContent>
            </Card>
            {loading && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography>Gerando invoice Lightning Network...</Typography>
              </Box>
            )}
          </Box>
        );
      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Invoice Lightning Network Gerado
            </Typography>
            <Card sx={{ mt: 2, backgroundColor: '#f5f5f5' }}>
              <CardContent>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                  {invoice}
                </Typography>
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <QrCodeIcon sx={{ fontSize: 120, color: '#1976d2' }} />
                </Box>
                <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
                  Escaneie o QR Code com sua carteira Lightning Network
                </Typography>
              </CardContent>
            </Card>
            {loading && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography>Aguardando confirmação do pagamento...</Typography>
              </Box>
            )}
          </Box>
        );
      case 3:
        return (
          <Box sx={{ textAlign: 'center' }}>
            <CheckCircleIcon sx={{ fontSize: 80, color: '#4caf50', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Pagamento Confirmado!
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Seus Bitcoins foram enviados para sua carteira.
            </Typography>
            <Card sx={{ backgroundColor: '#e8f5e8' }}>
              <CardContent>
                <Typography variant="body1">
                  <strong>Valor recebido:</strong> {(parseInt(amount) * 0.9 / 50000).toFixed(8)} BTC
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  <strong>Taxa de serviço:</strong> 10%
                </Typography>
              </CardContent>
            </Card>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle sx={{ 
        backgroundColor: '#1976d2', 
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: 1
      }}>
        <BitcoinIcon />
        Vender Bitcoin via Lightning Network
      </DialogTitle>
      
      <DialogContent sx={{ pt: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {renderStepContent(activeStep)}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose} color="inherit">
          Cancelar
        </Button>
        <Button 
          onClick={handleNext} 
          variant="contained"
          disabled={loading}
        >
          {activeStep === steps.length - 1 ? 'Finalizar' : 'Próximo'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default BitcoinModal; 