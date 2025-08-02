import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Container,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  QrCode as QrCodeIcon,
  CurrencyBitcoin as BitcoinIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

// Componente da Logo RedATM
const RedATMLogo = ({ size = 30, color = '#1e3c72' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
    <path
      d="M20 5 L35 35 L25 35 L20 25 L15 35 L5 35 Z"
      fill={color}
      stroke={color}
      strokeWidth="1"
    />
    <path
      d="M18 8 L22 8 Q25 8 25 12 Q25 16 22 16 L18 16 Q15 16 15 12 Q15 8 18 8 Z"
      fill="none"
      stroke={color}
      strokeWidth="2"
    />
    <path
      d="M16 10 L24 10 Q26 10 26 12 Q26 14 24 14 L16 14 Q14 14 14 12 Q14 10 16 10 Z"
      fill="none"
      stroke={color}
      strokeWidth="1.5"
    />
  </svg>
);

// Função para formatar valores em pesos argentinos
const formatPesos = (value) => {
  if (!value) return '';
  const numericValue = value.toString().replace(/[^\d]/g, '');
  if (numericValue === '') return '';
  
  const number = parseInt(numericValue);
  // Limitar a 250.000
  if (number > 250000) return '250.000';
  
  return number.toLocaleString('pt-BR');
};

// Função para converter string formatada de volta para número
const parseFormattedValue = (formattedValue) => {
  if (!formattedValue) return 0;
  return parseInt(formattedValue.replace(/[^\d]/g, ''));
};

function BitcoinFlow({ onClose, onBack }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [amount, setAmount] = useState('');
  const [btcPrice, setBtcPrice] = useState(null);
  const [btcAmount, setBtcAmount] = useState(0);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [loading, setLoading] = useState(false);

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
        setBtcPrice(50000);
      } finally {
        setLoadingPrice(false);
      }
    };

    fetchBtcPrice();
  }, []);

  // Calcular conversão em tempo real
  useEffect(() => {
    if (btcPrice && amount) {
      const arsAmount = parseFormattedValue(amount);
      if (arsAmount > 0) {
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

  const handleAmountChange = (e) => {
    const formattedValue = formatPesos(e.target.value);
    setAmount(formattedValue);
  };

  const handleCancel = () => {
    onBack(); // Volta para a tela principal, cancelando toda a operação
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    } else {
      onBack();
    }
  };

  const handleNext = () => {
    if (currentStep === 1) {
      const numericAmount = parseFormattedValue(amount);
      if (!numericAmount || numericAmount < 10000 || numericAmount > 250000) {
        return;
      }
      setCurrentStep(2);
    } else if (currentStep === 2) {
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        setCurrentStep(3);
      }, 2000);
    } else if (currentStep === 3) {
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        setCurrentStep(4);
      }, 3000);
    } else {
      onClose();
    }
  };

  const renderStep1 = () => (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Card sx={{ 
        backgroundColor: 'white', 
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: '#1e3c72', 
              fontWeight: 'bold', 
              mb: 3 
            }}
          >
            Ingresá el valor en pesos que querés recibir
          </Typography>
          
          <Typography 
            variant="body2" 
            sx={{ 
              color: '#6c757d', 
              mb: 4 
            }}
          >
            (múltiplos de 1.000) - Máximo: $250.000
          </Typography>

          <TextField
            fullWidth
            placeholder="0"
            value={amount}
            onChange={handleAmountChange}
            sx={{ 
              mb: 4,
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                fontSize: '1.2rem',
                textAlign: 'center'
              }
            }}
            InputProps={{
              startAdornment: '$ ',
            }}
          />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              fullWidth
              onClick={handleBack}
              sx={{
                borderRadius: '12px',
                borderColor: '#1e3c72',
                color: '#1e3c72',
                py: 1.5,
                textTransform: 'uppercase',
                fontWeight: 'bold'
              }}
            >
              CANCELAR
            </Button>
            <Button
              variant="contained"
              fullWidth
              onClick={handleNext}
              disabled={!parseFormattedValue(amount) || parseFormattedValue(amount) < 10000 || parseFormattedValue(amount) > 250000}
              sx={{
                borderRadius: '12px',
                backgroundColor: '#f7931a',
                py: 1.5,
                textTransform: 'uppercase',
                fontWeight: 'bold',
                '&:hover': {
                  backgroundColor: '#e67e22'
                }
              }}
            >
              ACEPTAR
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );

  const renderStep2 = () => {
    const numericAmount = parseFormattedValue(amount);
    const transactionCost = numericAmount * 0.1; // 10% de taxa
    const totalAmount = numericAmount + transactionCost;
    
    return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Card sx={{ 
          backgroundColor: 'white', 
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        }}>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <Typography 
              variant="h5" 
              sx={{ 
                color: '#1e3c72', 
                fontWeight: 'bold', 
                mb: 3 
              }}
            >
              Valor en pesos que vas a recibir
            </Typography>

            <Box sx={{ 
              backgroundColor: '#f8f9fa', 
              borderRadius: '12px', 
              p: 3, 
              mb: 3,
              border: '1px solid #dee2e6'
            }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1e3c72' }}>
                ${numericAmount.toLocaleString('pt-BR')}
              </Typography>
            </Box>

            <Typography 
              variant="body2" 
              sx={{ 
                color: '#6c757d', 
                mb: 2 
              }}
            >
              Esta transacción tiene un costo de ${transactionCost.toLocaleString('pt-BR')} (10%)
            </Typography>

            <Typography 
              variant="h6" 
              sx={{ 
                color: '#1e3c72', 
                fontWeight: 'bold', 
                mb: 2 
              }}
            >
              Valor total que se va a debitar de tu billetera: {btcAmount.toFixed(8)} BTC
            </Typography>

            <Typography 
              variant="body2" 
              sx={{ 
                color: '#6c757d', 
                mb: 2 
              }}
            >
              Bitcoin que vas a vender: {btcAmount.toFixed(8)} BTC
            </Typography>

            <Typography 
              variant="body2" 
              sx={{ 
                color: '#6c757d', 
                mb: 4 
              }}
            >
              Cotización Bitcoin: ${btcPrice?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} USD
            </Typography>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={handleBack}
                sx={{
                  borderRadius: '12px',
                  borderColor: '#1e3c72',
                  color: '#1e3c72',
                  py: 1.5,
                  textTransform: 'uppercase',
                  fontWeight: 'bold'
                }}
              >
                MODIFICAR
              </Button>
              <Button
                variant="contained"
                fullWidth
                onClick={handleNext}
                sx={{
                  borderRadius: '12px',
                  backgroundColor: '#f7931a',
                  py: 1.5,
                  textTransform: 'uppercase',
                  fontWeight: 'bold',
                  '&:hover': {
                    backgroundColor: '#e67e22'
                  }
                }}
              >
                CONFIRMAR
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
    );
  };

  const renderStep3 = () => (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Card sx={{ 
        backgroundColor: 'white', 
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Typography 
            variant="h6" 
            sx={{ 
              color: '#1e3c72', 
              fontWeight: 'bold', 
              mb: 3,
              lineHeight: 1.4
            }}
          >
            Si estás de acuerdo, escaneá el QR Code Lightning y
            <br />
            confirmá la venta desde la app de tu billetera Bitcoin
          </Typography>

          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            my: 4,
            p: 3,
            backgroundColor: '#f8f9fa',
            borderRadius: '12px'
          }}>
            <QrCodeIcon sx={{ fontSize: 200, color: '#1e3c72' }} />
          </Box>

          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2 }}>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              <Typography variant="body2" sx={{ color: '#6c757d' }}>
                Esperando confirmación...
              </Typography>
            </Box>
          )}

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              fullWidth
              onClick={handleCancel}
              sx={{
                borderRadius: '12px',
                borderColor: '#1e3c72',
                color: '#1e3c72',
                py: 1.5,
                textTransform: 'uppercase',
                fontWeight: 'bold'
              }}
            >
              CANCELAR
            </Button>
            <Button
              variant="contained"
              fullWidth
              onClick={handleNext}
              sx={{
                borderRadius: '12px',
                backgroundColor: '#f7931a',
                py: 1.5,
                textTransform: 'uppercase',
                fontWeight: 'bold',
                '&:hover': {
                  backgroundColor: '#e67e22'
                }
              }}
            >
              CONTINUAR
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );

  const renderStep4 = () => (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Card sx={{ 
        backgroundColor: 'white', 
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            mb: 3,
            p: 2,
            backgroundColor: '#e8f5e8',
            borderRadius: '12px',
            border: '1px solid #4caf50'
          }}>
            <CheckCircleIcon sx={{ fontSize: 40, color: '#4caf50', mr: 2 }} />
            <Typography variant="h6" sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
              Tu venta de Bitcoin fue completada
            </Typography>
          </Box>

          <Typography 
            variant="h5" 
            sx={{ 
              color: '#1e3c72', 
              fontWeight: 'bold', 
              mb: 2 
            }}
          >
            ¿Querés imprimir tu comprobante?
          </Typography>

          <Typography 
            variant="body2" 
            sx={{ 
              color: '#6c757d', 
              mb: 4 
            }}
          >
            Usando menos papel, colaborás con la preservación del medio ambiente
          </Typography>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              fullWidth
              onClick={handleCancel}
              sx={{
                borderRadius: '12px',
                borderColor: '#1e3c72',
                color: '#1e3c72',
                py: 1.5,
                textTransform: 'uppercase',
                fontWeight: 'bold'
              }}
            >
              NO
            </Button>
            <Button
              variant="contained"
              fullWidth
              onClick={handleNext}
              sx={{
                borderRadius: '12px',
                backgroundColor: '#f7931a',
                py: 1.5,
                textTransform: 'uppercase',
                fontWeight: 'bold',
                '&:hover': {
                  backgroundColor: '#e67e22'
                }
              }}
            >
              SÍ
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      backgroundColor: '#1e3c72',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#1e3c72', boxShadow: 'none' }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBack}
            sx={{ color: 'white', textTransform: 'uppercase', fontWeight: 'bold' }}
          >
            VOLTAR
          </Button>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RedATMLogo size={30} color="#1e3c72" />
            <Box>
              <Typography variant="h6" sx={{ color: '#1e3c72', fontWeight: 'bold' }}>
                RedATM
              </Typography>
              <Typography variant="caption" sx={{ color: '#6c757d' }}>
                Mucho más que un cajero.
              </Typography>
            </Box>
          </Box>

          <Button
            endIcon={<CloseIcon />}
            onClick={onClose}
            sx={{ color: 'white', textTransform: 'uppercase', fontWeight: 'bold' }}
          >
            SAIR
          </Button>
        </Toolbar>
      </AppBar>

      {/* Content */}
      <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}
        {currentStep === 4 && renderStep4()}
      </Box>
    </Box>
  );
}

export default BitcoinFlow; 