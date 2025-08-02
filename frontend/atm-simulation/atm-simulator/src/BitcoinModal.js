import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  Chip
} from '@mui/material';
import {
  CurrencyBitcoin as BitcoinIcon,
  QrCode as QrCodeIcon,
  CheckCircle as CheckCircleIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

const steps = ['Informar Valor', 'Gerar Invoice', 'Aguardar Pagamento', 'Confirmar'];

function BitcoinModal({ open, onClose }) {
  const [activeStep, setActiveStep] = useState(0);
  const [amount, setAmount] = useState('');
  const [sessionCode, setSessionCode] = useState('');
  const [invoice, setInvoice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [btcPrice, setBtcPrice] = useState(null);
  const [btcAmount, setBtcAmount] = useState(0);
  const [loadingPrice, setLoadingPrice] = useState(false);

  // Buscar cotação do Bitcoin na Binance
  useEffect(() => {
    const fetchBtcPrice = async () => {
      setLoadingPrice(true);
      try {
        const response = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
        const data = await response.json();
        const price = parseFloat(data.price);
        setBtcPrice(price);
      } catch (error) {
        console.error('Erro ao buscar cotação:', error);
        // Fallback para cotação simulada se a API falhar
        setBtcPrice(50000);
      } finally {
        setLoadingPrice(false);
      }
    };

    if (open) {
      fetchBtcPrice();
    }
  }, [open]);

  // Calcular conversão em tempo real
  useEffect(() => {
    if (btcPrice && amount) {
      const arsAmount = parseFloat(amount);
      if (!isNaN(arsAmount) && arsAmount > 0) {
        // Taxa de serviço de 10%
        const netAmount = arsAmount * 0.9;
        // Converter para BTC (assumindo 1 USD = 1000 ARS para simulação)
        const usdAmount = netAmount / 1000;
        const btcCalculated = usdAmount / btcPrice;
        setBtcAmount(btcCalculated);
      } else {
        setBtcAmount(0);
      }
    } else {
      setBtcAmount(0);
    }
  }, [amount, btcPrice]);

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

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Informe o valor em ARS que deseja vender em Bitcoin
            </Typography>
            
            {/* Cotação do Bitcoin */}
            <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
              <TrendingUpIcon sx={{ color: '#f7931a' }} />
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Cotação Bitcoin: 
              </Typography>
              {loadingPrice ? (
                <CircularProgress size={16} />
              ) : btcPrice ? (
                <Chip 
                  label={`$${btcPrice.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} USD`}
                  color="primary"
                  size="small"
                />
              ) : (
                <Chip label="Erro na cotação" color="error" size="small" />
              )}
            </Box>

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
            
            {/* Conversão em tempo real */}
            {amount && btcAmount > 0 && (
              <Card sx={{ mt: 2, backgroundColor: '#f8f9fa', border: '1px solid #e9ecef' }}>
                <CardContent>
                  <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                    Conversão em tempo real:
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1">
                      <strong>${parseInt(amount).toLocaleString('pt-BR')} ARS</strong>
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#f7931a', fontWeight: 'bold' }}>
                      → {btcAmount.toFixed(8)} BTC
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
                    Taxa de serviço: 10% | Taxa de câmbio: 1 USD = 1000 ARS
                  </Typography>
                </CardContent>
              </Card>
            )}

            <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
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
                  <strong>BTC Esperado:</strong> {btcAmount.toFixed(8)} BTC
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  <strong>Cotação BTC:</strong> ${btcPrice?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} USD
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
                  <strong>Valor recebido:</strong> {btcAmount.toFixed(8)} BTC
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  <strong>Taxa de serviço:</strong> 10%
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  <strong>Cotação no momento:</strong> ${btcPrice?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} USD
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
