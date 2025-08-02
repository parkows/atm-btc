import React, { useState } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid, 
  Container,
  AppBar,
  Toolbar
} from '@mui/material';
import {
  CreditCard as CreditCardIcon,
  QrCode as QrCodeIcon,
  Phone as PhoneIcon,
  AttachMoney as MoneyIcon,
  CurrencyBitcoin as BitcoinIcon,
  AccountBalance as AccountBalanceIcon
} from '@mui/icons-material';
import BitcoinFlow from './BitcoinFlow';
import './App.css';

// Componente da Logo RedATM
const RedATMLogo = ({ size = 40, color = '#1e3c72' }) => (
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

function App() {
  const [selectedCard, setSelectedCard] = useState(null);
  const [showBitcoinFlow, setShowBitcoinFlow] = useState(false);

  const handleCardClick = (cardId) => {
    setSelectedCard(cardId);
    if (cardId === 'bitcoin') {
      setShowBitcoinFlow(true);
    }
  };

  const handleCloseBitcoinFlow = () => {
    setShowBitcoinFlow(false);
    setSelectedCard(null);
  };

  const handleBackFromBitcoinFlow = () => {
    setShowBitcoinFlow(false);
    setSelectedCard(null);
  };

  const cards = [
    {
      id: 'card',
      title: 'OPERACIONES CON TARJETA',
      icon: <CreditCardIcon sx={{ fontSize: 40, color: '#1e3c72' }} />,
      logos: ['VISA', 'mastercard'],
      color: '#ffffff',
      disabled: false
    },
    {
      id: 'qr',
      title: 'RETIRÁ CON QR',
      icon: <QrCodeIcon sx={{ fontSize: 40, color: '#1e3c72' }} />,
      color: '#ffffff',
      disabled: false
    },
    {
      id: 'recharge',
      title: 'RECARGÁ',
      icon: <PhoneIcon sx={{ fontSize: 40, color: '#1e3c72' }} />,
      logos: ['SUBE', 'Movistar', 'personal', 'personal Pay', 'Claro'],
      color: '#ffffff',
      disabled: false
    },
    {
      id: 'pix',
      title: 'SAQUE COM PIX (Brasil)',
      icon: <AccountBalanceIcon sx={{ fontSize: 40, color: '#1e3c72' }} />,
      logos: ['pix'],
      color: '#ffffff',
      disabled: false
    },
    {
      id: 'deposits',
      title: 'DEPÓSITOS',
      icon: <MoneyIcon sx={{ fontSize: 40, color: '#ffffff' }} />,
      color: '#6c757d',
      disabled: true
    },
    {
      id: 'bitcoin',
      title: 'VENDER BITCOIN',
      icon: <BitcoinIcon sx={{ fontSize: 40, color: '#f7931a' }} />,
      subtitle: 'Red Lightning',
      color: '#ffffff',
      highlight: true,
      disabled: false
    }
  ];

  // Se o fluxo de Bitcoin estiver ativo, mostrar apenas o BitcoinFlow
  if (showBitcoinFlow) {
    return (
      <BitcoinFlow 
        onClose={handleCloseBitcoinFlow}
        onBack={handleBackFromBitcoinFlow}
      />
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      backgroundColor: '#1e3c72',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Main Content */}
      <Container maxWidth="lg" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 4 }}>
        {/* Cards Grid */}
        <Grid container spacing={3} sx={{ flexGrow: 1, mb: 4 }}>
          {cards.map((card) => (
            <Grid item xs={12} sm={6} md={4} key={card.id}>
              <Card 
                sx={{ 
                  height: 200,
                  backgroundColor: card.color,
                  cursor: card.disabled ? 'default' : 'pointer',
                  transition: 'all 0.3s ease',
                  transform: selectedCard === card.id ? 'scale(1.02)' : 'scale(1)',
                  boxShadow: selectedCard === card.id ? '0 8px 25px rgba(0,0,0,0.3)' : '0 4px 15px rgba(0,0,0,0.2)',
                  border: card.highlight ? '3px solid #f7931a' : 'none',
                  borderRadius: '16px',
                  '&:hover': {
                    transform: card.disabled ? 'scale(1)' : 'scale(1.02)',
                    boxShadow: card.disabled ? '0 4px 15px rgba(0,0,0,0.2)' : '0 8px 25px rgba(0,0,0,0.3)'
                  }
                }}
                onClick={() => !card.disabled && handleCardClick(card.id)}
              >
                <CardContent sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: 'center',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 3
                }}>
                  {card.icon}
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      mt: 2, 
                      fontWeight: 'bold',
                      color: card.disabled ? '#ffffff' : '#1e3c72',
                      fontSize: '1rem',
                      textTransform: 'uppercase',
                      lineHeight: 1.2
                    }}
                  >
                    {card.title}
                  </Typography>
                  {card.subtitle && (
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#f7931a',
                        fontWeight: 'bold',
                        mt: 1,
                        fontSize: '0.8rem'
                      }}
                    >
                      {card.subtitle}
                    </Typography>
                  )}
                  {card.logos && (
                    <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
                      {card.logos.map((logo, index) => (
                        <Typography 
                          key={index} 
                          variant="caption" 
                          sx={{ 
                            backgroundColor: card.disabled ? '#495057' : '#f8f9fa',
                            color: card.disabled ? '#ffffff' : '#1e3c72',
                            padding: '4px 8px',
                            borderRadius: '6px',
                            fontSize: '0.7rem',
                            fontWeight: 'bold',
                            border: card.disabled ? '1px solid #6c757d' : '1px solid #dee2e6'
                          }}
                        >
                          {logo}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Footer */}
      <Box sx={{ 
        backgroundColor: 'rgba(0,0,0,0.1)', 
        py: 3, 
        px: 4,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        {/* RedATM Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ 
            width: 50, 
            height: 50, 
            backgroundColor: 'white', 
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            p: 1
          }}>
            <RedATMLogo size={40} color="#1e3c72" />
          </Box>
          <Box>
            <Typography 
              variant="h5" 
              sx={{ 
                color: '#1e3c72', 
                fontWeight: 'bold', 
                mb: 0.5,
                fontSize: '1.5rem',
                letterSpacing: '0.5px'
              }}
            >
              RedATM
            </Typography>
            <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
              Mucho más que un cajero.
            </Typography>
          </Box>
        </Box>

        {/* CONVENIOS Button */}
        <Button 
          variant="outlined" 
          sx={{ 
            borderColor: '#1e3c72', 
            color: '#1e3c72',
            backgroundColor: 'white',
            borderRadius: '20px',
            px: 3,
            py: 1,
            fontWeight: 'bold',
            textTransform: 'uppercase',
            '&:hover': {
              borderColor: '#1e3c72',
              backgroundColor: '#f8f9fa'
            }
          }}
        >
          CONVENIOS
        </Button>
      </Box>
    </Box>
  );
}

export default App;
